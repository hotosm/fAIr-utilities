#!/usr/bin/env python3
"""
Production-ready validation script for fAIr-utilities.

This script performs comprehensive validation of the integrated fAIr-utilities
package to ensure it meets production standards.
"""

import sys
import traceback
import inspect
import time
from typing import List, Dict, Any


def test_comprehensive_imports():
    """Test all expected imports are available."""
    print("🔍 Testing comprehensive imports...")
    
    try:
        import hot_fair_utilities as fair
        print("✅ Main module imported successfully")
        
        # Expected attributes with categories
        expected_attrs = {
            'core_functions': [
                'georeference', 'evaluate', 'predict', 'polygonize', 'vectorize',
                'preprocess', 'yolo_v8_v1', 'bbox2tiles', 'tms2img'
            ],
            'integrated_functions': [
                'download_tiles', 'download_osm_data', 'VectorizeMasks', 
                'orthogonalize_gdf', 'predict_with_tiles'
            ],
            'training_functions': [
                'ramp_train', 'yolo_v8_v1_train', 'yolo_v8_v2_train'
            ],
            'configuration': [
                'config', 'DEFAULT_OAM_TMS_MOSAIC', 'DEFAULT_RAMP_MODEL', 
                'DEFAULT_YOLO_MODEL_V1', 'DEFAULT_YOLO_MODEL_V2'
            ],
            'monitoring': [
                'logger', 'performance_monitor', 'ProgressTracker'
            ],
            'validation': [
                'ValidationError', 'SecurityError', 'validate_bbox', 
                'validate_zoom_level', 'validate_confidence', 'validate_area_threshold'
            ]
        }
        
        missing_attrs = []
        for category, attrs in expected_attrs.items():
            print(f"\n  Testing {category}:")
            for attr in attrs:
                if hasattr(fair, attr):
                    print(f"    ✅ {attr}")
                else:
                    print(f"    ❌ {attr} - MISSING")
                    missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"\n⚠️  Missing attributes: {missing_attrs}")
            return False
        else:
            print("\n✅ All expected attributes available")
            return True
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False


def test_configuration_system():
    """Test configuration system."""
    print("\n🔍 Testing configuration system...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test config object
        config = fair.config
        print(f"✅ Configuration loaded: {type(config)}")
        
        # Test configuration validation
        issues = config.validate()
        if issues:
            print(f"⚠️  Configuration issues: {issues}")
        else:
            print("✅ Configuration validation passed")
        
        # Test environment detection
        print(f"✅ Environment: {config.environment}")
        print(f"✅ Debug mode: {config.debug}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_validation_system():
    """Test input validation system."""
    print("\n🔍 Testing validation system...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test bbox validation
        valid_bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        validated_bbox = fair.validate_bbox(valid_bbox)
        print(f"✅ Valid bbox validation: {validated_bbox}")
        
        # Test invalid bbox
        try:
            fair.validate_bbox([180, 90, -180, -90])  # Invalid order
            print("❌ Invalid bbox should have failed")
            return False
        except fair.ValidationError:
            print("✅ Invalid bbox correctly rejected")
        
        # Test zoom validation
        valid_zoom = fair.validate_zoom_level(18)
        print(f"✅ Valid zoom validation: {valid_zoom}")
        
        # Test confidence validation
        valid_confidence = fair.validate_confidence(0.5)
        print(f"✅ Valid confidence validation: {valid_confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        traceback.print_exc()
        return False


def test_async_functionality():
    """Test async function signatures."""
    print("\n🔍 Testing async functionality...")
    
    try:
        import hot_fair_utilities as fair
        
        async_functions = [
            'download_tiles',
            'download_osm_data', 
            'predict_with_tiles'
        ]
        
        all_async = True
        for func_name in async_functions:
            if hasattr(fair, func_name):
                func = getattr(fair, func_name)
                if inspect.iscoroutinefunction(func):
                    print(f"✅ {func_name} is properly async")
                else:
                    print(f"❌ {func_name} is not async")
                    all_async = False
            else:
                print(f"❌ {func_name} not found")
                all_async = False
        
        return all_async
        
    except Exception as e:
        print(f"❌ Async functionality test failed: {e}")
        return False


def test_monitoring_system():
    """Test monitoring and logging system."""
    print("\n🔍 Testing monitoring system...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test logger
        logger = fair.logger
        logger.info("Test log message")
        print("✅ Logger working")
        
        # Test performance monitor
        monitor = fair.performance_monitor
        monitor.start_timer("test_operation")
        time.sleep(0.1)
        duration = monitor.end_timer("test_operation")
        print(f"✅ Performance monitor working: {duration:.3f}s")
        
        # Test progress tracker
        with fair.ProgressTracker(10, "Test operation") as tracker:
            for i in range(10):
                tracker.update()
        print("✅ Progress tracker working")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        traceback.print_exc()
        return False


def test_class_instantiation():
    """Test class instantiation."""
    print("\n🔍 Testing class instantiation...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test TileSource
        from hot_fair_utilities.data_acquisition import TileSource
        tile_source = TileSource("https://example.com/{z}/{x}/{y}.png")
        print("✅ TileSource instantiated")
        
        # Test VectorizeMasks
        vectorizer = fair.VectorizeMasks(algorithm="rasterio")
        print("✅ VectorizeMasks instantiated")
        
        # Test with different algorithms
        try:
            vectorizer_potrace = fair.VectorizeMasks(algorithm="potrace")
            print("✅ VectorizeMasks with Potrace instantiated")
        except Exception as e:
            print(f"⚠️  VectorizeMasks with Potrace failed (expected if Potrace not installed): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Class instantiation test failed: {e}")
        traceback.print_exc()
        return False


def test_utility_functions():
    """Test utility functions."""
    print("\n🔍 Testing utility functions...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test get_tiles
        bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        tiles = fair.get_tiles(zoom=10, bbox=bbox)
        print(f"✅ get_tiles returned {len(tiles)} tiles")
        
        # Test get_geometry
        geometry = fair.get_geometry(bbox=bbox)
        print(f"✅ get_geometry returned {geometry['type']} geometry")
        
        return True
        
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        traceback.print_exc()
        return False


def test_security_features():
    """Test security features."""
    print("\n🔍 Testing security features...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test URL validation
        try:
            fair.validation.validate_url("http://localhost/test")
            print("❌ Localhost URL should be blocked")
            return False
        except fair.SecurityError:
            print("✅ Localhost URL correctly blocked")
        
        # Test file path validation
        try:
            fair.validation.validate_file_path("../../../etc/passwd")
            print("❌ Path traversal should be blocked")
            return False
        except fair.SecurityError:
            print("✅ Path traversal correctly blocked")
        
        # Test large bbox rejection
        try:
            fair.validate_bbox([-180, -90, 180, 90])  # Entire world
            print("❌ Large bbox should be rejected")
            return False
        except fair.ValidationError:
            print("✅ Large bbox correctly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        traceback.print_exc()
        return False


def generate_production_report():
    """Generate comprehensive production readiness report."""
    print("🏭 PRODUCTION READINESS ASSESSMENT")
    print("=" * 60)
    
    tests = [
        ("Comprehensive Imports", test_comprehensive_imports),
        ("Configuration System", test_configuration_system),
        ("Validation System", test_validation_system),
        ("Async Functionality", test_async_functionality),
        ("Monitoring System", test_monitoring_system),
        ("Class Instantiation", test_class_instantiation),
        ("Utility Functions", test_utility_functions),
        ("Security Features", test_security_features),
    ]
    
    passed = 0
    total = len(tests)
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            results[test_name] = False
            print(f"💥 {test_name}: CRASHED - {e}")
    
    # Generate final report
    print("\n" + "=" * 60)
    print("📊 PRODUCTION READINESS REPORT")
    print("=" * 60)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    # Categorize results
    critical_tests = [
        "Comprehensive Imports", "Configuration System", 
        "Validation System", "Security Features"
    ]
    
    critical_passed = sum(1 for test in critical_tests if results.get(test, False))
    
    print(f"Critical tests passed: {critical_passed}/{len(critical_tests)}")
    
    # Determine production readiness
    if passed == total:
        print("\n🎉 PRODUCTION READY!")
        print("✅ All tests passed - Ready for production deployment")
        status = "READY"
    elif critical_passed == len(critical_tests) and passed >= total * 0.8:
        print("\n⚠️  MOSTLY READY")
        print("✅ Critical functionality works")
        print("⚠️  Some non-critical issues found")
        status = "MOSTLY_READY"
    elif critical_passed >= len(critical_tests) * 0.8:
        print("\n⚠️  NEEDS WORK")
        print("⚠️  Some critical issues found")
        print("❌ Not recommended for production")
        status = "NEEDS_WORK"
    else:
        print("\n❌ NOT READY")
        print("❌ Critical issues prevent production use")
        print("🔧 Requires immediate attention")
        status = "NOT_READY"
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    if status == "READY":
        print("- Deploy to production")
        print("- Monitor performance and logs")
        print("- Set up alerting and monitoring")
    elif status == "MOSTLY_READY":
        print("- Fix non-critical issues")
        print("- Deploy to staging for further testing")
        print("- Monitor closely in production")
    else:
        print("- Fix critical issues before deployment")
        print("- Run additional testing")
        print("- Review failed tests above")
    
    return status == "READY"


def main():
    """Main function."""
    print("🔍 fAIr-utilities Production Validation")
    print("=" * 50)
    
    success = generate_production_report()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
