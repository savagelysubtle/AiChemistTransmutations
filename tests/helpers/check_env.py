#!/usr/bin/env python3
"""Check the environment."""

import subprocess
import sys
from pathlib import Path

def check_python():
    """Check Python version."""
    print(f"Python version: {sys.version}")
    return True

def check_uv():
    """Check if uv is available."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        print(f"UV version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ UV not found")
        return False

def check_pytest():
    """Check if pytest is available."""
    try:
        result = subprocess.run(["uv", "run", "pytest", "--version"], capture_output=True, text=True)
        print(f"Pytest version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Pytest not available: {e}")
        return False

def check_project_structure():
    """Check project structure."""
    project_dir = Path(__file__).parent
    
    required_dirs = [
        "src/transmutation_codex",
        "tests",
        "tests/unit",
        "tests/integration"
    ]
    
    for dir_path in required_dirs:
        full_path = project_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            return False
    
    return True

def main():
    """Check environment."""
    print("🔍 Checking Environment")
    print("=" * 30)
    
    checks = [
        check_python,
        check_uv,
        check_pytest,
        check_project_structure
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Check {check.__name__} failed: {e}")
            failed += 1
    
    print(f"\nPassed: {passed}, Failed: {failed}")
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)