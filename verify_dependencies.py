#!/usr/bin/env python3
"""
Comprehensive dependency verification script for fAIr-utilities.

This script verifies that all required dependencies are properly installed
and can be imported successfully.
"""

import sys
import importlib


def test_dependency(module_name, package_name=None, version_attr="__version__"):
    """Test if a dependency can be imported and get its version."""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, version_attr, "unknown")
        print(f"✅ {package_name or module_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: MISSING ({e})")
        return False


def main():
    """Verify all dependencies."""
    print("🔍 Verifying fAIr-utilities dependencies...")
    print("=" * 60)
    
    # Core dependencies
    print("\n📦 Core Dependencies:")
    core_deps = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("shapely", "shapely"),
        ("geopandas", "geopandas"),
        ("rasterio", "rasterio"),
        ("mercantile", "mercantile"),
        ("tqdm", "tqdm"),
        ("PIL", "Pillow"),
        ("matplotlib", "matplotlib"),
    ]
    
    core_passed = 0
    for module, package in core_deps:
        if test_dependency(module, package):
            core_passed += 1
    
    # GDAL dependency (special case)
    print("\n🌍 Geospatial Dependencies:")
    gdal_passed = 0
    try:
        from osgeo import gdal
        print(f"✅ GDAL/osgeo: {gdal.VersionInfo()}")
        gdal_passed = 1
    except ImportError as e:
        print(f"❌ GDAL/osgeo: MISSING ({e})")
    
    # Computer vision dependencies
    print("\n🤖 Computer Vision Dependencies:")
    cv_deps = [
        ("cv2", "opencv-python-headless"),
        ("torch", "torch"),
        ("torchvision", "torchvision"),
        ("ultralytics", "ultralytics"),
    ]
    
    cv_passed = 0
    for module, package in cv_deps:
        if test_dependency(module, package):
            cv_passed += 1
    
    # Optional dependencies
    print("\n📦 Optional Dependencies:")
    optional_deps = [
        ("fairpredictor", "fairpredictor"),
        ("geoml_toolkits", "geoml-toolkits"),
        ("tensorflow", "tensorflow"),
    ]
    
    optional_passed = 0
    for module, package in optional_deps:
        if test_dependency(module, package):
            optional_passed += 1
    
    # Test hot_fair_utilities import
    print("\n🎯 Package Import Test:")
    try:
        import hot_fair_utilities as fair
        print("✅ hot_fair_utilities: Import successful")
        
        # Test specific modules
        try:
            from hot_fair_utilities.georeferencing import georeference
            print("✅ georeferencing module: Import successful")
        except ImportError as e:
            print(f"❌ georeferencing module: {e}")
        
        package_passed = 1
    except ImportError as e:
        print(f"❌ hot_fair_utilities: Import failed ({e})")
        package_passed = 0
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPENDENCY VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_core = len(core_deps)
    total_cv = len(cv_deps)
    total_optional = len(optional_deps)
    
    print(f"Core Dependencies: {core_passed}/{total_core}")
    print(f"GDAL: {gdal_passed}/1")
    print(f"Computer Vision: {cv_passed}/{total_cv}")
    print(f"Optional Packages: {optional_passed}/{total_optional}")
    print(f"Package Import: {package_passed}/1")
    
    # Calculate overall status
    required_passed = core_passed + gdal_passed + package_passed
    required_total = total_core + 1 + 1
    
    print(f"\nRequired Dependencies: {required_passed}/{required_total}")
    
    if required_passed == required_total:
        print("🎉 ALL REQUIRED DEPENDENCIES VERIFIED!")
        print("✅ fAIr-utilities is ready to use")
        return 0
    else:
        print("❌ SOME REQUIRED DEPENDENCIES ARE MISSING")
        print("🔧 Install missing dependencies and try again")
        
        # Provide installation hints
        if core_passed < total_core or gdal_passed == 0:
            print("\n💡 Installation hints:")
            print("pip install -r requirements-build.txt")
            if gdal_passed == 0:
                print("sudo apt-get install gdal-bin libgdal-dev")
                print("pip install GDAL==$(gdal-config --version)")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
