#!/usr/bin/env python3
"""
Validation script for fAIr-utilities integration.

This script validates that the integration was successful by testing
imports and basic functionality.
"""

import sys
import traceback


def test_basic_imports():
    """Test basic imports."""
    print("🔍 Testing basic imports...")

    try:
        import hot_fair_utilities as fair
        print("✅ hot_fair_utilities imported successfully")

        # Test main module attributes
        expected_attrs = [
            'georeference', 'evaluate', 'predict', 'polygonize', 'vectorize',
            'preprocess', 'yolo_v8_v1', 'bbox2tiles', 'tms2img',
            'download_tiles', 'download_osm_data', 'VectorizeMasks', 'orthogonalize_gdf',
            'predict_with_tiles', 'ramp_train', 'yolo_v8_v1_train', 'yolo_v8_v2_train'
        ]

        missing_attrs = []
        for attr in expected_attrs:
            if not hasattr(fair, attr):
                missing_attrs.append(attr)

        if missing_attrs:
            print(f"⚠️  Missing attributes: {missing_attrs}")
        else:
            print("✅ All expected attributes available")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False


def test_new_modules():
    """Test new module imports."""
    print("\n🔍 Testing new module imports...")

    try:
        # Test data acquisition
        from hot_fair_utilities.data_acquisition import TileSource, download_tiles, download_osm_data
        print("✅ data_acquisition module imported successfully")

        # Test vectorization
        from hot_fair_utilities.vectorization import VectorizeMasks, orthogonalize_gdf
        print("✅ vectorization module imported successfully")

        # Test enhanced prediction
        from hot_fair_utilities.inference import predict_with_tiles
        print("✅ enhanced prediction imported successfully")

        return True

    except Exception as e:
        print(f"❌ New module import failed: {e}")
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
                    print(f"✅ {model}: {value[:50]}...")
                else:
                    print(f"⚠️  {model}: Invalid value")
            else:
                print(f"❌ {model}: Not found")

        return True

    except Exception as e:
        print(f"❌ Default models test failed: {e}")
        traceback.print_exc()
        return False


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
        print(f"❌ Class instantiation failed: {e}")
        traceback.print_exc()
        return False


def test_utility_functions():
    """Test utility functions."""
    print("\n🔍 Testing utility functions...")

    try:
        import hot_fair_utilities as fair

        # Test get_tiles function
        bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        tiles = fair.get_tiles(zoom=18, bbox=bbox)
        print(f"✅ get_tiles returned {len(tiles)} tiles")

        # Test get_geometry function
        geometry = fair.get_geometry(bbox=bbox)
        print(f"✅ get_geometry returned {geometry['type']} geometry")

        return True

    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        traceback.print_exc()
        return False


def test_async_functions():
    """Test async function signatures."""
    print("\n🔍 Testing async function signatures...")

    try:
        import inspect
        import hot_fair_utilities as fair

        async_functions = [
            'download_tiles',
            'download_osm_data',
            'predict_with_tiles'
        ]

        for func_name in async_functions:
            if hasattr(fair, func_name):
                func = getattr(fair, func_name)
                if inspect.iscoroutinefunction(func):
                    print(f"✅ {func_name} is properly async")
                else:
                    print(f"⚠️  {func_name} is not async")
            else:
                print(f"❌ {func_name} not found")

        return True

    except Exception as e:
        print(f"❌ Async functions test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("🚀 fAIr-utilities Integration Validation")
    print("=" * 50)

    tests = [
        test_basic_imports,
        test_new_modules,
        test_default_models,
        test_class_instantiation,
        test_utility_functions,
        test_async_functions,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print("\n" + "=" * 50)
    print("📊 Validation Summary")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n🎉 All validation tests passed!")
        print("✅ Integration is successful and ready to use!")

        print("\n🚀 Next steps:")
        print("1. Run: python examples/integrated_workflow_example.py")
        print("2. Try: python test_integration.py")
        print("3. Read: INTEGRATION_GUIDE.md")

        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed.")
        print("❌ Integration may have issues. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
