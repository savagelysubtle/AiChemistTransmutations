"""Gumroad webhook server for automatic license generation.

This server listens for Gumroad purchase events and automatically:
1. Generates a license key
2. Stores it in Supabase
3. Emails it to the customer (via Gumroad)

Deployment:
    - Railway/Render: git push deployment
    - AWS Lambda: Serverless framework
    - DigitalOcean App Platform: Docker deployment

Environment Variables Required:
    - GUMROAD_WEBHOOK_SECRET: Secret from Gumroad dashboard
    - SUPABASE_URL: Supabase project URL
    - SUPABASE_SERVICE_KEY: Service role key (admin access)
    - PRIVATE_KEY_PATH: Path to RSA private key for signing

Usage:
    python scripts/gumroad/webhook_server.py

Or with Gunicorn:
    gunicorn scripts.gumroad.webhook_server:app
"""

import hashlib
import hmac
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transmutation_codex.core.licensing.crypto import LicenseCrypto
from transmutation_codex.core.licensing.supabase_backend import SupabaseBackend

app = Flask(__name__)

# Configuration
GUMROAD_WEBHOOK_SECRET = os.getenv("GUMROAD_WEBHOOK_SECRET")
PRIVATE_KEY_PATH = os.getenv(
    "PRIVATE_KEY_PATH", "scripts/licensing/keys/private_key.pem"
)

# Product ID mapping (configure these to match your Gumroad product permalinks)
# Format: "gumroad-permalink": {"type": "license_type", "max_activations": count}
# Update these values to match your actual Gumroad product permalinks!
PRODUCT_MAP = {
    "transmutation-codex-basic": {"type": "basic", "max_activations": 1},
    "transmutation-codex-pro": {"type": "pro", "max_activations": 3},
    "transmutation-codex-enterprise": {"type": "enterprise", "max_activations": 10},
}


def load_private_key() -> bytes:
    """Load private key for license signing."""
    key_path = Path(PRIVATE_KEY_PATH)
    if not key_path.exists():
        raise FileNotFoundError(f"Private key not found: {key_path}")
    with open(key_path, "rb") as f:
        return f.read()


def verify_gumroad_signature(payload: bytes, signature: str) -> bool:
    """Verify Gumroad webhook signature.

    Args:
        payload: Raw request body
        signature: X-Gumroad-Signature header

    Returns:
        True if signature is valid
    """
    if not GUMROAD_WEBHOOK_SECRET:
        # In development, skip verification
        return True

    computed = hmac.new(
        GUMROAD_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


def generate_and_store_license(
    email: str, product_id: str, order_id: str, customer_name: str | None = None
) -> dict:
    """Generate license and store in Supabase.

    Args:
        email: Customer email
        product_id: Gumroad product permalink
        order_id: Gumroad sale ID
        customer_name: Optional customer name

    Returns:
        Dictionary with license info

    Raises:
        ValueError: If product_id is not recognized
    """
    # Get license type from product map
    product_config = PRODUCT_MAP.get(product_id)
    if not product_config:
        raise ValueError(f"Unknown product ID: {product_id}")

    license_type = product_config["type"]
    max_activations = product_config["max_activations"]

    # Generate license
    crypto = LicenseCrypto()
    private_key = load_private_key()

    license_data = {
        "email": email,
        "type": license_type,
        "max_activations": max_activations,
        "issued_at": datetime.now().isoformat(),
        "version": "1.0",
        "order_id": order_id,
    }

    if customer_name:
        license_data["name"] = customer_name

    license_key = crypto.generate_license_key(license_data, private_key)

    # Store in Supabase
    backend = SupabaseBackend()
    result = (
        backend.client.table("licenses")
        .insert(
            {
                "email": email,
                "license_key": license_key,
                "type": license_type,
                "max_activations": max_activations,
                "order_id": order_id,
                "status": "active",
                "created_at": datetime.now().isoformat(),
            }
        )
        .execute()
    )

    return {
        "license_key": license_key,
        "email": email,
        "type": license_type,
        "max_activations": max_activations,
        "order_id": order_id,
    }


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "aichemist-webhook"}), 200


@app.route("/webhook/gumroad", methods=["POST"])
def gumroad_webhook():
    """Handle Gumroad purchase webhook.

    Expected Gumroad POST data:
        - sale_id: Unique sale ID
        - product_id: Product permalink
        - email: Customer email
        - full_name: Customer name (optional)
        - price: Sale price
        - recurrence: Subscription info (if applicable)
    """
    # Verify signature
    signature = request.headers.get("X-Gumroad-Signature", "")
    if not verify_gumroad_signature(request.data, signature):
        app.logger.warning(f"Invalid signature from {request.remote_addr}")
        return jsonify({"error": "Invalid signature"}), 401

    # Parse form data (Gumroad sends form-encoded, not JSON)
    data = request.form.to_dict()

    # Extract purchase info
    email = data.get("email")
    product_id = data.get("product_id")  # Product permalink
    order_id = data.get("sale_id")
    customer_name = data.get("full_name")

    if not email or not product_id:
        app.logger.error(f"Missing required fields: {data}")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Generate and store license
        license_info = generate_and_store_license(
            email, product_id, order_id, customer_name
        )

        app.logger.info(f"License generated: {order_id} for {email} ({product_id})")

        # Return license key to Gumroad
        # Gumroad will automatically email this to the customer
        return (
            jsonify(
                {
                    "success": True,
                    "license_generated": True,
                    "order_id": order_id,
                    "license_key": license_info["license_key"],
                }
            ),
            200,
        )

    except ValueError as e:
        app.logger.error(f"Product validation error: {e}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        app.logger.error(f"License generation failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/webhook/test", methods=["POST"])
def test_webhook():
    """Test endpoint for development (no signature verification)."""
    if os.getenv("FLASK_ENV") != "development":
        return jsonify({"error": "Test endpoint only available in development"}), 403

    data = request.json

    email = data.get("email", "test@example.com")
    product_id = data.get("product_id", "aichemist_pro")
    order_id = data.get("order_id", f"TEST-{datetime.now().timestamp()}")

    try:
        license_info = generate_and_store_license(email, product_id, order_id)
        return jsonify({"success": True, **license_info}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
