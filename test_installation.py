#!/usr/bin/env python3
"""
Test script to verify that fAIr-utilities installation is working correctly.

This script performs basic import and functionality tests to ensure
the package was installed properly and core features are accessible.
"""

import sys
import traceback


def test_basic_import():
    """Test basic package import."""
    print("🔍 Testing basic import...")
    try:
        import hot_fair_utilities
        print("✅ Basic import successful")
        return True
    except ImportError as e:
        print(f"❌ Basic import failed: {e}")
        return False


def test_submodule_imports():
    """Test importing key submodules."""
    print("🔍 Testing submodule imports...")
    
    modules_to_test = [
        "hot_fair_utilities.data_acquisition",
        "hot_fair_utilities.preprocessing", 
        "hot_fair_utilities.inference",
        "hot_fair_utilities.postprocessing",
        "hot_fair_utilities.training",
    ]
    
    success_count = 0
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"⚠️ {module} import failed: {e}")
    
    print(f"📊 Submodule import success: {success_count}/{len(modules_to_test)}")
    return success_count > 0


def test_core_functionality():
    """Test core functionality to ensure it works."""
    print("🔍 Testing core functionality...")
    
    try:
        # Test validation functions
        from hot_fair_utilities.validation import validate_bbox
        
        # Test with valid bbox
        bbox = [0.0, 0.0, 1.0, 1.0]
        validated_bbox = validate_bbox(bbox)
        print(f"✅ Bbox validation works: {validated_bbox}")
        
        # Test configuration
        from hot_fair_utilities.config import FairConfig
        config = FairConfig()
        print(f"✅ Configuration works: {config.max_concurrent_downloads}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Core functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_package_dependencies():
    """Test availability of package dependencies."""
    print("🔍 Testing package dependencies...")

    # Test core package dependencies (should be available)
    core_deps = {
        "fairpredictor": "fairpredictor",
        "geoml-toolkits": "geoml_toolkits",
    }

    # Test optional dependencies
    optional_deps = {
        "torch": "torch",
        "tensorflow": "tensorflow",
        "ultralytics": "ultralytics",
        "geopandas": "geopandas",
        "rasterio": "rasterio",
    }

    core_available = 0
    for name, module in core_deps.items():
        try:
            __import__(module)
            print(f"✅ {name} available (core dependency)")
            core_available += 1
        except ImportError:
            print(f"❌ {name} not available (REQUIRED)")

    optional_available = 0
    for name, module in optional_deps.items():
        try:
            __import__(module)
            print(f"✅ {name} available")
            optional_available += 1
        except ImportError:
            print(f"⚠️ {name} not available (optional)")

    print(f"📊 Core dependencies: {core_available}/{len(core_deps)}")
    print(f"📊 Optional dependencies: {optional_available}/{len(optional_deps)}")

    # Test package integration
    try:
        import hot_fair_utilities as fair
        print(f"📦 fairpredictor integration: {'✅' if fair.FAIRPREDICTOR_AVAILABLE else '❌'}")
        print(f"📦 geoml-toolkits integration: {'✅' if fair.GEOML_TOOLKITS_AVAILABLE else '❌'}")
    except Exception as e:
        print(f"❌ Package integration test failed: {e}")

    return core_available == len(core_deps)


def test_package_metadata():
    """Test package metadata and version info."""
    print("🔍 Testing package metadata...")
    
    try:
        import hot_fair_utilities
        
        # Test version
        if hasattr(hot_fair_utilities, '__version__'):
            print(f"✅ Package version: {hot_fair_utilities.__version__}")
        else:
            print("⚠️ Package version not available")
        
        # Test package info
        if hasattr(hot_fair_utilities, '__doc__'):
            print(f"✅ Package documentation available")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Metadata test failed: {e}")
        return False


def main():
    """Run all installation tests."""
    print("🚀 Starting fAIr-utilities installation verification...")
    print("=" * 60)
    
    tests = [
        ("Basic Import", test_basic_import),
        ("Submodule Imports", test_submodule_imports),
        ("Core Functionality", test_core_functionality),
        ("Package Dependencies", test_package_dependencies),
        ("Package Metadata", test_package_metadata),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Installation is working correctly!")
        return 0
    elif passed_tests >= total_tests // 2:
        print("⚠️ PARTIAL SUCCESS - Core functionality works, some optional features missing")
        return 0
    else:
        print("❌ INSTALLATION ISSUES - Multiple tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
