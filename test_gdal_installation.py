#!/usr/bin/env python3
"""
Test script to verify GDAL installation and osgeo import.

This script performs comprehensive testing of GDAL installation
to ensure the osgeo module can be imported successfully.
"""

import sys
import subprocess


def test_gdal_system_installation():
    """Test that GDAL system packages are installed."""
    print("🔍 Testing GDAL system installation...")
    
    try:
        # Test gdal-config command
        result = subprocess.run(
            ["gdal-config", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        gdal_version = result.stdout.strip()
        print(f"✅ GDAL system version: {gdal_version}")
        return gdal_version
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GDAL system packages not installed")
        print("   Install with: sudo apt-get install gdal-bin libgdal-dev")
        return None


def test_osgeo_import():
    """Test that osgeo module can be imported."""
    print("🔍 Testing osgeo import...")
    
    try:
        from osgeo import gdal
        print("✅ osgeo.gdal import successful")
        
        # Test GDAL functionality
        gdal_version = gdal.VersionInfo()
        print(f"✅ GDAL Python bindings version: {gdal_version}")
        
        # Test basic GDAL functionality
        driver_count = gdal.GetDriverCount()
        print(f"✅ GDAL drivers available: {driver_count}")
        
        return True
    except ImportError as e:
        print(f"❌ osgeo import failed: {e}")
        return False


def test_hot_fair_utilities_import():
    """Test that hot_fair_utilities can be imported (which requires osgeo)."""
    print("🔍 Testing hot_fair_utilities import...")
    
    try:
        import hot_fair_utilities as fair
        print("✅ hot_fair_utilities import successful")
        
        # Test that georeferencing module is accessible
        from hot_fair_utilities.georeferencing import georeference
        print("✅ georeferencing module import successful")
        
        return True
    except ImportError as e:
        print(f"❌ hot_fair_utilities import failed: {e}")
        return False


def test_gdal_python_bindings_installation():
    """Test installing GDAL Python bindings if not available."""
    print("🔍 Testing GDAL Python bindings installation...")
    
    # Get system GDAL version
    gdal_version = test_gdal_system_installation()
    if not gdal_version:
        return False
    
    try:
        # Try to install GDAL Python bindings
        print(f"📦 Installing GDAL=={gdal_version}...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", f"GDAL=={gdal_version}"],
            check=True,
            capture_output=True
        )
        print("✅ GDAL Python bindings installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ GDAL Python bindings installation failed: {e}")
        return False


def main():
    """Run comprehensive GDAL tests."""
    print("🚀 Starting GDAL installation verification...")
    print("=" * 60)
    
    tests = [
        ("GDAL System Installation", test_gdal_system_installation),
        ("osgeo Import", test_osgeo_import),
        ("hot_fair_utilities Import", test_hot_fair_utilities_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
                # If osgeo import failed, try to fix it
                if test_name == "osgeo Import":
                    print("🔧 Attempting to fix GDAL Python bindings...")
                    if test_gdal_python_bindings_installation():
                        print("🔄 Retrying osgeo import...")
                        if test_osgeo_import():
                            passed += 1
                            print(f"✅ {test_name} PASSED (after fix)")
                        else:
                            print(f"❌ {test_name} still FAILED after fix")
                    
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 GDAL TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL GDAL TESTS PASSED - GDAL is working correctly!")
        print("\n✅ hot_fair_utilities should work without osgeo import errors")
        return 0
    else:
        print("❌ SOME GDAL TESTS FAILED")
        print("\n🔧 Troubleshooting steps:")
        print("1. Install system packages: sudo apt-get install gdal-bin libgdal-dev")
        print("2. Install Python bindings: pip install GDAL==$(gdal-config --version)")
        print("3. Verify installation: python -c 'from osgeo import gdal'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
