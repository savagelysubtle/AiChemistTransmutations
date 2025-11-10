"""Test script to diagnose license activation issue in Electron app.

This simulates how Electron calls the license_bridge.py script.
"""

import subprocess
import sys
from pathlib import Path

# Paths
project_root = Path(__file__).parent
script_path = project_root / "src" / "transmutation_codex" / "adapters" / "bridges" / "license_bridge.py"
venv_python = project_root / ".venv" / "Scripts" / "python.exe"

# License key
license_key = "AICHEMIST:T/nUi8R7rx5PJjRsx2YAfUUVgywuCabYKME5dkjTk7nh5QnlRpQY2YvWiPEu65pfLu/PbX31JVslNAo5ruihE46+5VgWtq9RroySjeE0TtCuUiwfonEtGFFXC4GsVvlTCSBy/q6HWL0yuBZea2nObMTx5jPltVHG+2Mufemu197NniIrjioRYnB9rHyrK7UxLkLtAphCL0dahoE/HR32nRcW6PsCzov9JgxDczrpxMvZa3KDrriToXy2nBic4zw7nMhY5QOs/gkRhstEvw0TDdEK9vXbmrB/qVyxh62H2VlKT4xyzVqbdtISQNJaanPwi79Y/Dn7K4P+gD2BD7hQgg==:eyJlbWFpbCI6ICJkZXZAYWljaGVtaXN0LmxvY2FsIiwgImZlYXR1cmVzIjogWyJhbGwiXSwgImlzc3VlZF9hdCI6ICIyMDI1LTEwLTIxVDEwOjI0OjE4LjMxNzk2MiIsICJsaWNlbnNlX3R5cGUiOiAiZW50ZXJwcmlzZSIsICJtYXhfYWN0aXZhdGlvbnMiOiA5OTl9"

print("🔍 Testing License Activation")
print(f"Python: {venv_python}")
print(f"Script: {script_path}")
print(f"License Key: {license_key[:50]}...")
print()

# Test 1: Check if Python exists
if not venv_python.exists():
    print("❌ Venv Python not found!")
    print(f"   Expected: {venv_python}")
    sys.exit(1)
else:
    print("✅ Venv Python found")

# Test 2: Check if script exists
if not script_path.exists():
    print("❌ License bridge script not found!")
    print(f"   Expected: {script_path}")
    sys.exit(1)
else:
    print("✅ License bridge script found")

# Test 3: Run the command
print("\n📞 Running license activation command...")
print(f"   Command: {venv_python} {script_path} activate \"{license_key[:30]}...\"")

result = subprocess.run(
    [str(venv_python), str(script_path), "activate", license_key],
    capture_output=True,
    text=True
)

print(f"\n📊 Result:")
print(f"   Exit Code: {result.returncode}")
print(f"\n   STDOUT:")
print(f"   {result.stdout}")
print(f"\n   STDERR:")
print(f"   {result.stderr}")

if result.returncode == 0:
    print("\n✅ License activation SUCCESSFUL!")
    import json
    data = json.loads(result.stdout)
    print(f"   Status: {data}")
else:
    print(f"\n❌ License activation FAILED with code {result.returncode}")
    print("   This is the same error you're seeing in Electron!")

