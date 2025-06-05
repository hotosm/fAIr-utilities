#!/usr/bin/env python3
"""
Simple test to verify matplotlib installation fix.

This script tests that matplotlib can be imported successfully
and that hot_fair_utilities can be imported without matplotlib errors.
"""

import sys


def test_matplotlib_import():
    """Test matplotlib import."""
    print("🔍 Testing matplotlib import...")
    try:
        import matplotlib
        print(f"✅ matplotlib import successful - version: {matplotlib.__version__}")
        return True
    except ImportError as e:
        print(f"❌ matplotlib import failed: {e}")
        return False


def test_matplotlib_pyplot():
    """Test matplotlib.pyplot import."""
    print("🔍 Testing matplotlib.pyplot import...")
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib.pyplot import successful")
        return True
    except ImportError as e:
        print(f"❌ matplotlib.pyplot import failed: {e}")
        return False


def test_hot_fair_utilities_with_matplotlib():
    """Test hot_fair_utilities import (which may use matplotlib)."""
    print("🔍 Testing hot_fair_utilities import...")
    try:
        import hot_fair_utilities as fair
        print("✅ hot_fair_utilities import successful")
        
        # Test that we can access basic functionality
        bbox = fair.validate_bbox([0.0, 0.0, 1.0, 1.0])
        print(f"✅ Basic functionality test: bbox validation works")
        
        return True
    except ImportError as e:
        print(f"❌ hot_fair_utilities import failed: {e}")
        return False


def main():
    """Run matplotlib fix verification tests."""
    print("🚀 Testing matplotlib installation fix...")
    print("=" * 50)
    
    tests = [
        ("matplotlib Import", test_matplotlib_import),
        ("matplotlib.pyplot Import", test_matplotlib_pyplot),
        ("hot_fair_utilities Import", test_hot_fair_utilities_with_matplotlib),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 MATPLOTLIB FIX TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 MATPLOTLIB FIX SUCCESSFUL!")
        print("✅ All matplotlib-related imports are working correctly")
        return 0
    else:
        print("❌ MATPLOTLIB FIX INCOMPLETE")
        print("🔧 Some matplotlib-related imports are still failing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
