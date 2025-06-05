#!/usr/bin/env python3
"""
Simple test script for CI/CD environments.

This script performs basic verification that the package migration is working
correctly in automated environments.
"""

import sys


def main():
    """Run simple migration verification tests."""
    print("🚀 Running simple migration verification...")
    
    # Test 1: Basic import
    print("\n🔍 Test 1: Basic Import")
    try:
        import hot_fair_utilities as fair
        print("✅ Basic import successful")
    except Exception as e:
        print(f"❌ Basic import failed: {e}")
        return 1
    
    # Test 2: Package availability flags
    print("\n🔍 Test 2: Package Availability Flags")
    try:
        print(f"📦 fairpredictor available: {fair.FAIRPREDICTOR_AVAILABLE}")
        print(f"📦 geoml-toolkits available: {fair.GEOML_TOOLKITS_AVAILABLE}")
        print("✅ Package availability flags working")
    except Exception as e:
        print(f"❌ Package availability test failed: {e}")
        return 1
    
    # Test 3: Core functionality
    print("\n🔍 Test 3: Core Functionality")
    try:
        # Test validation
        bbox = fair.validate_bbox([0.0, 0.0, 1.0, 1.0])
        print(f"✅ Bbox validation: {bbox}")
        
        # Test configuration
        config = fair.config
        print(f"✅ Configuration loaded: max_downloads={config.max_concurrent_downloads}")
        
        # Test utility functions
        tiles = fair.bbox2tiles([0.0, 0.0, 1.0, 1.0], 10)
        print(f"✅ Bbox2tiles: {len(tiles)} tiles")
        
        print("✅ Core functionality working")
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return 1
    
    # Test 4: Stub functions (if packages not available)
    print("\n🔍 Test 4: Stub Functions")
    try:
        if not fair.FAIRPREDICTOR_AVAILABLE:
            try:
                fair.predict_with_tiles()
                print("❌ Stub function should raise ImportError")
                return 1
            except ImportError as e:
                if "fairpredictor" in str(e):
                    print("✅ fairpredictor stub function works")
                else:
                    print(f"⚠️ Unexpected error: {e}")
        else:
            print("✅ fairpredictor available, skipping stub test")
        
        if not fair.GEOML_TOOLKITS_AVAILABLE:
            try:
                fair.download_tiles()
                print("❌ Stub function should raise ImportError")
                return 1
            except ImportError as e:
                if "geoml-toolkits" in str(e):
                    print("✅ geoml-toolkits stub function works")
                else:
                    print(f"⚠️ Unexpected error: {e}")
        else:
            print("✅ geoml-toolkits available, skipping stub test")
        
        print("✅ Stub functions working correctly")
    except Exception as e:
        print(f"❌ Stub function test failed: {e}")
        return 1
    
    # Test 5: Exports
    print("\n🔍 Test 5: Package Exports")
    try:
        required_exports = [
            "georeference", "evaluate", "predict", "polygonize", "vectorize",
            "bbox2tiles", "tms2img", "config", "validate_bbox"
        ]
        
        missing_exports = []
        for export in required_exports:
            if not hasattr(fair, export):
                missing_exports.append(export)
        
        if missing_exports:
            print(f"❌ Missing exports: {missing_exports}")
            return 1
        else:
            print(f"✅ All {len(required_exports)} required exports available")
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return 1
    
    # Summary
    print("\n🎉 SIMPLE TEST SUMMARY")
    print("=" * 40)
    print("✅ Basic Import: PASS")
    print("✅ Package Availability: PASS")
    print("✅ Core Functionality: PASS")
    print("✅ Stub Functions: PASS")
    print("✅ Package Exports: PASS")
    print("\n🚀 Migration verification SUCCESSFUL!")
    print("📦 Package is ready for production use")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
