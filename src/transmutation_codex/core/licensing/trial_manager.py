"""Trial period management and conversion tracking.

This module handles trial limitations including conversion counting
and provides trial status information to the application.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from ..exceptions import TrialExpiredError


class TrialManager:
    """Manage trial period and conversion limits."""

    # Trial configuration
    TRIAL_CONVERSION_LIMIT = 10  # Free users get 10 conversions
    TRIAL_DURATION_DAYS = 14  # Alternative: 14-day trial (not currently enforced)

    # Conversion types allowed in trial
    FREE_CONVERTERS = {"md2pdf"}  # Only MD→PDF allowed in free trial

    def __init__(self, data_dir: Path):
        """Initialize trial manager.

        Args:
            data_dir: Directory for storing trial data

        Example:
            >>> trial = TrialManager(Path("~/.aichemist"))
            >>> status = trial.get_trial_status()
            >>> print(f"Conversions remaining: {status['remaining']}")
        """
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # SQLite database for tracking conversions
        self.db_path = self.data_dir / "trial.db"
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for trial tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create conversions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                converter_name TEXT NOT NULL,
                input_file TEXT NOT NULL,
                output_file TEXT,
                timestamp TEXT NOT NULL,
                file_size_bytes INTEGER,
                success BOOLEAN NOT NULL
            )
        """)

        # Create trial_info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trial_info (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Set first_run date if not exists
        cursor.execute("SELECT value FROM trial_info WHERE key = 'first_run'")
        if not cursor.fetchone():
            first_run = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO trial_info (key, value) VALUES ('first_run', ?)",
                (first_run,),
            )

        conn.commit()
        conn.close()

    def record_conversion(
        self,
        converter_name: str,
        input_file: str,
        output_file: str | None = None,
        file_size_bytes: int | None = None,
        success: bool = True,
    ):
        """Record a conversion attempt.

        Args:
            converter_name: Name of converter used
            input_file: Input file path
            output_file: Output file path (if successful)
            file_size_bytes: Size of input file
            success: Whether conversion succeeded

        Raises:
            TrialExpiredError: If trial limit exceeded
        """
        # Check if trial is expired BEFORE recording
        if not self.can_convert(converter_name):
            status = self.get_trial_status()
            raise TrialExpiredError(
                "Trial limit exceeded. Please purchase a license to continue.",
                conversions_used=status["used"],
                trial_limit=self.TRIAL_CONVERSION_LIMIT,
            )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO conversions
            (converter_name, input_file, output_file, timestamp, file_size_bytes, success)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                converter_name,
                input_file,
                output_file,
                datetime.now().isoformat(),
                file_size_bytes,
                success,
            ),
        )

        conn.commit()
        conn.close()

    def get_conversion_count(self, successful_only: bool = True) -> int:
        """Get total number of conversions performed.

        Args:
            successful_only: Count only successful conversions

        Returns:
            Number of conversions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if successful_only:
            cursor.execute("SELECT COUNT(*) FROM conversions WHERE success = 1")
        else:
            cursor.execute("SELECT COUNT(*) FROM conversions")

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_trial_status(self) -> dict:
        """Get current trial status.

        Returns:
            Dictionary with trial information:
            - status: "active" | "expired"
            - used: Number of conversions used
            - limit: Maximum conversions allowed
            - remaining: Conversions remaining
            - first_run: Date of first run
            - days_since_first_run: Days since installation

        Example:
            >>> status = trial.get_trial_status()
            >>> if status['status'] == 'expired':
            ...     print("Trial expired!")
        """
        used = self.get_conversion_count()
        remaining = max(0, self.TRIAL_CONVERSION_LIMIT - used)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM trial_info WHERE key = 'first_run'")
        first_run_str = cursor.fetchone()[0]
        conn.close()

        first_run = datetime.fromisoformat(first_run_str)
        days_since = (datetime.now() - first_run).days

        status: Literal["active", "expired"] = (
            "expired" if remaining == 0 else "active"
        )

        return {
            "status": status,
            "used": used,
            "limit": self.TRIAL_CONVERSION_LIMIT,
            "remaining": remaining,
            "first_run": first_run_str,
            "days_since_first_run": days_since,
        }

    def can_convert(self, converter_name: str) -> bool:
        """Check if user can perform a conversion.

        Args:
            converter_name: Name of converter to check

        Returns:
            True if conversion is allowed
        """
        # Check if converter is in free tier
        if converter_name in self.FREE_CONVERTERS:
            # Check conversion limit
            status = self.get_trial_status()
            return status["remaining"] > 0

        # Paid-only converter
        return False

    def reset_trial(self):
        """Reset trial data (for testing purposes only).

        WARNING: This should only be used in development/testing.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM conversions")
        cursor.execute("DELETE FROM trial_info WHERE key = 'first_run'")
        cursor.execute(
            "INSERT INTO trial_info (key, value) VALUES ('first_run', ?)",
            (datetime.now().isoformat(),),
        )

        conn.commit()
        conn.close()

    def get_conversion_history(self, limit: int = 50) -> list[dict]:
        """Get recent conversion history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of conversion records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT converter_name, input_file, output_file, timestamp,
                   file_size_bytes, success
            FROM conversions
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )

        records = []
        for row in cursor.fetchall():
            records.append(
                {
                    "converter_name": row[0],
                    "input_file": row[1],
                    "output_file": row[2],
                    "timestamp": row[3],
                    "file_size_bytes": row[4],
                    "success": bool(row[5]),
                }
            )

        conn.close()
        return records
