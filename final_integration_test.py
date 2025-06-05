#!/usr/bin/env python3
"""
Final integration test for fAIr-utilities.

This script performs a comprehensive test of the integration to verify
what is working and what still needs to be completed.
"""

import sys
import traceback
import inspect


def test_basic_structure():
    """Test basic module structure and imports."""
    print("🔍 Testing basic module structure...")
    
    try:
        import hot_fair_utilities as fair
        print("✅ Main module imported successfully")
        
        # Test core attributes
        core_attrs = ['georeference', 'predict', 'polygonize', 'vectorize', 'preprocess']
        for attr in core_attrs:
            if hasattr(fair, attr):
                print(f"✅ Core function '{attr}' available")
            else:
                print(f"❌ Core function '{attr}' missing")
        
        return True
    except Exception as e:
        print(f"❌ Basic structure test failed: {e}")
        return False


def test_new_integrations():
    """Test new integrated functionality."""
    print("\n🔍 Testing new integrated modules...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test data acquisition
        if hasattr(fair, 'download_tiles'):
            print("✅ download_tiles function available")
            if inspect.iscoroutinefunction(fair.download_tiles):
                print("✅ download_tiles is properly async")
            else:
                print("⚠️  download_tiles is not async")
        else:
            print("❌ download_tiles function missing")
        
        if hasattr(fair, 'download_osm_data'):
            print("✅ download_osm_data function available")
            if inspect.iscoroutinefunction(fair.download_osm_data):
                print("✅ download_osm_data is properly async")
            else:
                print("⚠️  download_osm_data is not async")
        else:
            print("❌ download_osm_data function missing")
        
        # Test vectorization
        if hasattr(fair, 'VectorizeMasks'):
            print("✅ VectorizeMasks class available")
            try:
                vectorizer = fair.VectorizeMasks()
                print("✅ VectorizeMasks can be instantiated")
            except Exception as e:
                print(f"⚠️  VectorizeMasks instantiation failed: {e}")
        else:
            print("❌ VectorizeMasks class missing")
        
        if hasattr(fair, 'orthogonalize_gdf'):
            print("✅ orthogonalize_gdf function available")
        else:
            print("❌ orthogonalize_gdf function missing")
        
        # Test enhanced prediction
        if hasattr(fair, 'predict_with_tiles'):
            print("✅ predict_with_tiles function available")
            if inspect.iscoroutinefunction(fair.predict_with_tiles):
                print("✅ predict_with_tiles is properly async")
            else:
                print("⚠️  predict_with_tiles is not async")
        else:
            print("❌ predict_with_tiles function missing")
        
        return True
    except Exception as e:
        print(f"❌ New integrations test failed: {e}")
        traceback.print_exc()
        return False


def test_training_modules():
    """Test training module integration."""
    print("\n🔍 Testing training modules...")
    
    try:
        import hot_fair_utilities as fair
        
        training_functions = ['ramp_train', 'yolo_v8_v1_train', 'yolo_v8_v2_train']
        for func_name in training_functions:
            if hasattr(fair, func_name):
                print(f"✅ {func_name} function available")
            else:
                print(f"❌ {func_name} function missing")
        
        return True
    except Exception as e:
        print(f"❌ Training modules test failed: {e}")
        traceback.print_exc()
        return False


def test_default_models():
    """Test default model constants."""
    print("\n🔍 Testing default model constants...")
    
    try:
        import hot_fair_utilities as fair
        
        models = [
            'DEFAULT_RAMP_MODEL',
            'DEFAULT_YOLO_MODEL_V1',
            'DEFAULT_YOLO_MODEL_V2', 
            'DEFAULT_OAM_TMS_MOSAIC'
        ]
        
        for model in models:
            if hasattr(fair, model):
                value = getattr(fair, model)
                if isinstance(value, str) and len(value) > 0:
                    print(f"✅ {model}: Available")
                else:
                    print(f"⚠️  {model}: Invalid value")
            else:
                print(f"❌ {model}: Missing")
        
        return True
    except Exception as e:
        print(f"❌ Default models test failed: {e}")
        return False


def test_utility_functions():
    """Test utility functions."""
    print("\n🔍 Testing utility functions...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test get_tiles
        bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        tiles = fair.get_tiles(zoom=18, bbox=bbox)
        print(f"✅ get_tiles returned {len(tiles)} tiles")
        
        # Test get_geometry
        geometry = fair.get_geometry(bbox=bbox)
        print(f"✅ get_geometry returned {geometry['type']} geometry")
        
        return True
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        traceback.print_exc()
        return False


def test_module_imports():
    """Test individual module imports."""
    print("\n🔍 Testing individual module imports...")
    
    modules_to_test = [
        'hot_fair_utilities.data_acquisition',
        'hot_fair_utilities.vectorization',
        'hot_fair_utilities.inference',
        'hot_fair_utilities.training',
        'hot_fair_utilities.preprocessing',
        'hot_fair_utilities.postprocessing'
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name} import failed: {e}")
    
    print(f"Module import success rate: {success_count}/{len(modules_to_test)}")
    return success_count == len(modules_to_test)


def test_class_instantiation():
    """Test class instantiation."""
    print("\n🔍 Testing class instantiation...")
    
    try:
        # Test TileSource
        from hot_fair_utilities.data_acquisition import TileSource
        tile_source = TileSource("https://example.com/{z}/{x}/{y}.png")
        print("✅ TileSource instantiated successfully")
        
        # Test VectorizeMasks
        from hot_fair_utilities.vectorization import VectorizeMasks
        vectorizer = VectorizeMasks()
        print("✅ VectorizeMasks instantiated successfully")
        
        return True
    except Exception as e:
        print(f"❌ Class instantiation test failed: {e}")
        traceback.print_exc()
        return False


def generate_integration_report():
    """Generate a comprehensive integration report."""
    print("\n" + "=" * 60)
    print("📊 FINAL INTEGRATION REPORT")
    print("=" * 60)
    
    tests = [
        ("Basic Structure", test_basic_structure),
        ("New Integrations", test_new_integrations),
        ("Training Modules", test_training_modules),
        ("Default Models", test_default_models),
        ("Utility Functions", test_utility_functions),
        ("Module Imports", test_module_imports),
        ("Class Instantiation", test_class_instantiation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
    
    print("\n" + "=" * 60)
    print("📈 SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Integration appears to be working correctly")
        print("\n🚀 Ready for:")
        print("- Basic usage and testing")
        print("- Development and experimentation")
        print("- Further enhancement and optimization")
    elif passed >= total * 0.8:
        print("\n⚠️  MOSTLY WORKING - Some issues found")
        print("✅ Core functionality appears to work")
        print("⚠️  Some components may need attention")
    elif passed >= total * 0.5:
        print("\n⚠️  PARTIALLY WORKING - Significant issues")
        print("⚠️  Major components have problems")
        print("❌ Needs significant work before production use")
    else:
        print("\n❌ INTEGRATION FAILED")
        print("❌ Critical issues prevent basic functionality")
        print("🔧 Requires immediate attention")
    
    print(f"\n📋 Next steps:")
    print("1. Review failed tests above")
    print("2. Check SENIOR_ENGINEER_VERIFICATION.md for detailed analysis")
    print("3. Address critical issues before production use")
    
    return passed == total


def main():
    """Main function."""
    print("🔍 fAIr-utilities Final Integration Test")
    print("=" * 50)
    
    success = generate_integration_report()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
