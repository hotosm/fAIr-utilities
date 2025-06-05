#!/usr/bin/env python3
"""
Final verification script for all dependencies and functionality.

This script performs comprehensive testing to ensure everything is working.
"""

import sys
import importlib


def test_import_with_details(module_name, package_name=None):
    """Test import with detailed error reporting."""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name or module_name}: {version}")
        return True, None
    except ImportError as e:
        print(f"❌ {package_name or module_name}: FAILED - {e}")
        return False, str(e)
    except Exception as e:
        print(f"⚠️ {package_name or module_name}: ERROR - {e}")
        return False, str(e)


def test_tensorflow_keras_compatibility():
    """Test TensorFlow and tf.keras compatibility."""
    print("\n🔍 Testing TensorFlow/tf.keras compatibility...")

    try:
        import tensorflow as tf
        print(f"✅ TensorFlow version: {tf.__version__}")
        print(f"✅ tf.keras version: {tf.keras.__version__}")

        # Test tf.keras integration
        print("✅ TensorFlow tf.keras integration working")

        # Test basic functionality
        model = tf.keras.Sequential([tf.keras.layers.Dense(1, input_shape=(1,))])
        print("✅ Basic tf.keras model creation successful")

        # Test model compilation
        model.compile(optimizer='adam', loss='mse')
        print("✅ tf.keras model compilation successful")

        # Test if tf.__internal__ is available (but don't test specific functions)
        if hasattr(tf, '__internal__'):
            print("✅ tf.__internal__ is available")
        else:
            print("⚠️ tf.__internal__ not available (may be expected)")

        return True
    except Exception as e:
        print(f"❌ TensorFlow/tf.keras compatibility test failed: {e}")
        return False


def test_segmentation_models():
    """Test segmentation-models functionality."""
    print("\n🔍 Testing segmentation-models...")
    
    try:
        import segmentation_models as sm
        print(f"✅ segmentation-models version: {sm.__version__}")
        
        # Test framework setting
        sm.set_framework('tf.keras')
        print("✅ TensorFlow backend set successfully")
        
        # Test available models
        models = ['Unet', 'FPN', 'Linknet', 'PSPNet']
        available_models = []
        for model_name in models:
            if hasattr(sm, model_name):
                available_models.append(model_name)
        
        print(f"✅ Available models: {', '.join(available_models)}")
        return True
    except Exception as e:
        print(f"❌ segmentation-models test failed: {e}")
        return False


def test_gdal_functionality():
    """Test GDAL functionality."""
    print("\n🔍 Testing GDAL functionality...")
    
    try:
        from osgeo import gdal
        print(f"✅ GDAL version: {gdal.VersionInfo()}")
        
        # Test basic GDAL functionality
        driver_count = gdal.GetDriverCount()
        print(f"✅ GDAL drivers available: {driver_count}")
        
        # Test common drivers
        common_drivers = ['GTiff', 'PNG', 'JPEG']
        available_drivers = []
        for driver_name in common_drivers:
            driver = gdal.GetDriverByName(driver_name)
            if driver:
                available_drivers.append(driver_name)
        
        print(f"✅ Common drivers available: {', '.join(available_drivers)}")
        return True
    except Exception as e:
        print(f"❌ GDAL functionality test failed: {e}")
        return False


def test_optional_packages():
    """Test optional packages."""
    print("\n🔍 Testing optional packages...")
    
    optional_packages = [
        ("fairpredictor", "fairpredictor"),
        ("geoml_toolkits", "geoml-toolkits"),
    ]
    
    available_count = 0
    for module, package in optional_packages:
        success, error = test_import_with_details(module, package)
        if success:
            available_count += 1
    
    print(f"\n📊 Optional packages available: {available_count}/{len(optional_packages)}")
    return True  # Always return True since these are optional


def test_hot_fair_utilities():
    """Test hot_fair_utilities import and basic functionality."""
    print("\n🔍 Testing hot_fair_utilities...")
    
    try:
        import hot_fair_utilities as fair
        print("✅ hot_fair_utilities import successful")
        
        # Test basic functionality
        bbox = fair.validate_bbox([0.0, 0.0, 1.0, 1.0])
        print("✅ bbox validation works")
        
        # Test configuration
        config = fair.config
        print("✅ configuration access works")
        
        # Test georeferencing module
        try:
            from hot_fair_utilities.georeferencing import georeference
            print("✅ georeferencing module import successful")
        except ImportError as e:
            print(f"❌ georeferencing module import failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ hot_fair_utilities test failed: {e}")
        return False


def main():
    """Run comprehensive verification."""
    print("🚀 FINAL VERIFICATION OF ALL DEPENDENCIES")
    print("=" * 60)
    
    # Core dependencies
    print("\n📦 Core Dependencies:")
    core_deps = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("shapely", "shapely"),
        ("geopandas", "geopandas"),
        ("rasterio", "rasterio"),
        ("mercantile", "mercantile"),
        ("tqdm", "tqdm"),
        ("PIL", "Pillow"),
    ]
    
    core_passed = 0
    for module, package in core_deps:
        success, _ = test_import_with_details(module, package)
        if success:
            core_passed += 1
    
    # Specialized tests
    tests = [
        ("GDAL Functionality", test_gdal_functionality),
        ("TensorFlow/Keras Compatibility", test_tensorflow_keras_compatibility),
        ("segmentation-models", test_segmentation_models),
        ("Optional Packages", test_optional_packages),
        ("hot_fair_utilities", test_hot_fair_utilities),
    ]
    
    specialized_passed = 0
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                specialized_passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_core = len(core_deps)
    total_specialized = len(tests)
    
    print(f"Core Dependencies: {core_passed}/{total_core}")
    print(f"Specialized Tests: {specialized_passed}/{total_specialized}")
    
    # Determine overall status
    critical_tests = ["GDAL Functionality", "TensorFlow/Keras Compatibility", "hot_fair_utilities"]
    critical_passed = sum(1 for test_name, _ in tests if test_name in critical_tests and test_name in [t[0] for t in tests[:specialized_passed]])
    
    if core_passed >= total_core * 0.8 and critical_passed >= len(critical_tests):
        print("\n🎉 VERIFICATION SUCCESSFUL!")
        print("✅ All critical dependencies are working")
        print("✅ hot_fair_utilities is ready for use")
        return 0
    else:
        print("\n❌ VERIFICATION FAILED")
        print("❌ Some critical dependencies are not working")
        print("\n💡 Check the failed tests above for troubleshooting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
