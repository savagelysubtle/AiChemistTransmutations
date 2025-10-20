#!/usr/bin/env python3
"""Test runner for the Transmutation Codex test suite."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite."""
    print("🧪 Running Transmutation Codex Test Suite")
    print("=" * 50)
    
    # Test categories
    test_categories = [
        ("Unit Tests - Converters", "tests/unit/test_converters/"),
        ("Unit Tests - Core Systems", "tests/unit/test_*.py"),
        ("Integration Tests", "tests/integration/"),
        ("All Tests", "tests/")
    ]
    
    results = {}
    
    for category_name, test_path in test_categories:
        print(f"\n📋 Running {category_name}")
        print("-" * 30)
        
        try:
            # Run pytest
            cmd = [
                "uv", "run", "pytest", 
                test_path,
                "-v",
                "--tb=short",
                "--color=yes"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            
            results[category_name] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ {category_name} PASSED")
            else:
                print(f"❌ {category_name} FAILED")
                print("STDOUT:")
                print(result.stdout)
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)
                    
        except Exception as e:
            print(f"❌ Error running {category_name}: {e}")
            results[category_name] = {
                "returncode": 1,
                "stdout": "",
                "stderr": str(e)
            }
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for category_name, result in results.items():
        if result["returncode"] == 0:
            print(f"✅ {category_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {category_name}: FAILED")
            failed += 1
    
    print(f"\nTotal: {passed + failed} categories")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test categories failed")
        return False


def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"🧪 Running specific test: {test_file}")
    print("=" * 50)
    
    try:
        cmd = [
            "uv", "run", "pytest", 
            test_file,
            "-v",
            "--tb=short",
            "--color=yes"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Run specific test
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()