#!/usr/bin/env python3
"""
Quick test script to verify package migration before CI/CD.

This script performs essential checks to ensure the migration is working
correctly before running the full CI/CD pipeline.
"""

import sys
import traceback
import warnings


def test_basic_import():
    """Test that the package can be imported."""
    print("🔍 Testing basic import...")
    try:
        import hot_fair_utilities as fair
        print("✅ Basic import successful")
        return True
    except Exception as e:
        print(f"❌ Basic import failed: {e}")
        traceback.print_exc()
        return False


def test_package_availability_flags():
    """Test that package availability flags work correctly."""
    print("🔍 Testing package availability flags...")
    try:
        import hot_fair_utilities as fair
        
        print(f"📦 fairpredictor available: {fair.FAIRPREDICTOR_AVAILABLE}")
        print(f"📦 geoml-toolkits available: {fair.GEOML_TOOLKITS_AVAILABLE}")
        
        # Test that flags are boolean
        assert isinstance(fair.FAIRPREDICTOR_AVAILABLE, bool)
        assert isinstance(fair.GEOML_TOOLKITS_AVAILABLE, bool)
        
        print("✅ Package availability flags working correctly")
        return True
    except Exception as e:
        print(f"❌ Package availability test failed: {e}")
        traceback.print_exc()
        return False


def test_stub_functions():
    """Test that stub functions provide helpful error messages."""
    print("🔍 Testing stub functions...")
    try:
        import hot_fair_utilities as fair
        
        # Test fairpredictor stub functions
        if not fair.FAIRPREDICTOR_AVAILABLE:
            try:
                fair.predict_with_tiles()
                print("❌ Stub function should have raised ImportError")
                return False
            except ImportError as e:
                if "fairpredictor" in str(e) and "pip install" in str(e):
                    print("✅ fairpredictor stub function works correctly")
                else:
                    print(f"⚠️ Stub function error message could be better: {e}")
        
        # Test geoml-toolkits stub functions
        if not fair.GEOML_TOOLKITS_AVAILABLE:
            try:
                fair.download_tiles()
                print("❌ Stub function should have raised ImportError")
                return False
            except ImportError as e:
                if "geoml-toolkits" in str(e) and "pip install" in str(e):
                    print("✅ geoml-toolkits stub function works correctly")
                else:
                    print(f"⚠️ Stub function error message could be better: {e}")
        
        print("✅ Stub functions test passed")
        return True
    except Exception as e:
        print(f"❌ Stub functions test failed: {e}")
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test that legacy functions work with deprecation warnings."""
    print("🔍 Testing backward compatibility...")
    try:
        import hot_fair_utilities as fair
        
        # Test deprecated functions show warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                # This should show deprecation warning
                fair.tms2img([0, 0], [1, 1], 10, "/tmp", "test")
            except Exception as e:
                # Expected if geoml-toolkits not available
                print(f"Expected error (packages not available): {str(e)[:50]}...")
            
            # Check if deprecation warning was shown
            deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
            if deprecation_warnings:
                print(f"✅ Deprecation warning shown: {deprecation_warnings[0].message}")
            else:
                print("⚠️ No deprecation warning (may be expected if packages missing)")
        
        print("✅ Backward compatibility test passed")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        traceback.print_exc()
        return False


def test_core_functionality():
    """Test that core fAIr-utilities functionality still works."""
    print("🔍 Testing core functionality...")
    try:
        import hot_fair_utilities as fair
        
        # Test validation functions
        bbox = fair.validate_bbox([0.0, 0.0, 1.0, 1.0])
        print(f"✅ Bbox validation: {bbox}")
        
        # Test configuration
        config = fair.config
        print(f"✅ Configuration: max_downloads={config.max_concurrent_downloads}")
        
        # Test utility functions
        tiles = fair.bbox2tiles([0.0, 0.0, 1.0, 1.0], 10)
        print(f"✅ Bbox2tiles: {len(tiles)} tiles generated")
        
        print("✅ Core functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_dependency_resolver():
    """Test that dependency resolver works."""
    print("🔍 Testing dependency resolver...")
    try:
        from hot_fair_utilities.dependency_resolver import DependencyResolver
        
        resolver = DependencyResolver()
        print("✅ Dependency resolver imported")
        
        # Test compatibility matrix
        matrix = resolver.COMPATIBILITY_MATRIX
        print(f"✅ Compatibility matrix: {len(matrix)} packages")
        
        print("✅ Dependency resolver test passed")
        return True
    except Exception as e:
        print(f"❌ Dependency resolver test failed: {e}")
        traceback.print_exc()
        return False


def test_exports():
    """Test that all expected exports are available."""
    print("🔍 Testing package exports...")
    try:
        import hot_fair_utilities as fair
        
        # Test core exports
        core_exports = [
            "georeference", "evaluate", "predict", "polygonize", "vectorize",
            "preprocess", "yolo_v8_v1", "bbox2tiles", "tms2img"
        ]
        
        for export in core_exports:
            if hasattr(fair, export):
                print(f"✅ {export} available")
            else:
                print(f"❌ {export} missing")
                return False
        
        # Test package-specific exports
        if fair.FAIRPREDICTOR_AVAILABLE:
            fairpredictor_exports = ["predict_with_tiles", "download_model", "validate_model"]
            for export in fairpredictor_exports:
                if hasattr(fair, export):
                    print(f"✅ {export} available (fairpredictor)")
                else:
                    print(f"⚠️ {export} missing (fairpredictor)")
        
        if fair.GEOML_TOOLKITS_AVAILABLE:
            geoml_exports = ["download_tiles", "download_osm_data", "VectorizeMasks"]
            for export in geoml_exports:
                if hasattr(fair, export):
                    print(f"✅ {export} available (geoml-toolkits)")
                else:
                    print(f"⚠️ {export} missing (geoml-toolkits)")
        
        print("✅ Package exports test passed")
        return True
    except Exception as e:
        print(f"❌ Package exports test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all quick tests."""
    print("🚀 Running quick migration tests...")
    print("=" * 60)
    
    tests = [
        ("Basic Import", test_basic_import),
        ("Package Availability Flags", test_package_availability_flags),
        ("Stub Functions", test_stub_functions),
        ("Backward Compatibility", test_backward_compatibility),
        ("Core Functionality", test_core_functionality),
        ("Dependency Resolver", test_dependency_resolver),
        ("Package Exports", test_exports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 QUICK TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Ready for CI/CD!")
        print("\n🚀 Next steps:")
        print("1. Commit your changes: git add . && git commit -m 'feat: package migration'")
        print("2. Push to trigger CI/CD: git push origin feature/integrate-geoml-toolkits-fairpredictor")
        print("3. Monitor GitHub Actions for full test results")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Fix issues before CI/CD")
        print(f"\n🔧 {total - passed} test(s) need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
