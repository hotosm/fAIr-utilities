#!/usr/bin/env python3
"""
Test script to check Python 3.12 compatibility issues.

This script identifies common Python 3.12 compatibility problems,
particularly the pkgutil.ImpImporter issue.
"""

import sys
import importlib


def check_python_version():
    """Check Python version and warn about 3.12 issues."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 12:
        print("⚠️ Python 3.12+ detected - checking for compatibility issues...")
        return True
    else:
        print("✅ Python version < 3.12 - should have fewer compatibility issues")
        return False


def test_pkgutil_compatibility():
    """Test pkgutil module for Python 3.12 compatibility."""
    print("\n🔍 Testing pkgutil compatibility...")
    
    try:
        import pkgutil
        print("✅ pkgutil module imported successfully")
        
        # Check for deprecated ImpImporter
        if hasattr(pkgutil, 'ImpImporter'):
            print("✅ pkgutil.ImpImporter is available")
        else:
            print("❌ pkgutil.ImpImporter is NOT available (removed in Python 3.12)")
            print("   This may cause issues with older packages that use it")
        
        # Check for zipimporter (suggested replacement)
        if hasattr(pkgutil, 'zipimporter'):
            print("✅ pkgutil.zipimporter is available")
        else:
            print("⚠️ pkgutil.zipimporter is NOT available")
        
        # Test basic pkgutil functionality
        modules = list(pkgutil.iter_modules())
        print(f"✅ pkgutil.iter_modules() works - found {len(modules)} modules")
        
        return True
    except Exception as e:
        print(f"❌ pkgutil test failed: {e}")
        return False


def test_common_dependencies():
    """Test common dependencies for Python 3.12 compatibility."""
    print("\n🔍 Testing common dependencies for Python 3.12 compatibility...")
    
    dependencies = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("PIL", "Pillow"),
        ("shapely", "shapely"),
        ("rasterio", "rasterio"),
        ("geopandas", "geopandas"),
        ("tqdm", "tqdm"),
        ("mercantile", "mercantile"),
    ]
    
    passed = 0
    failed = []
    
    for module_name, package_name in dependencies:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {package_name}: {version}")
            passed += 1
        except ImportError as e:
            print(f"❌ {package_name}: Import failed - {e}")
            failed.append(package_name)
        except Exception as e:
            print(f"⚠️ {package_name}: Other error - {e}")
            failed.append(package_name)
    
    print(f"\n📊 Dependency test results: {passed}/{len(dependencies)} passed")
    if failed:
        print(f"❌ Failed dependencies: {', '.join(failed)}")
    
    return len(failed) == 0


def test_tensorflow_compatibility():
    """Test TensorFlow compatibility with Python 3.12."""
    print("\n🔍 Testing TensorFlow compatibility...")
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow imported successfully - version: {tf.__version__}")
        
        # Test basic TensorFlow functionality
        x = tf.constant([1, 2, 3, 4])
        print(f"✅ TensorFlow basic operations work: {x}")
        
        # Test tf.keras
        model = tf.keras.Sequential([tf.keras.layers.Dense(1)])
        print("✅ tf.keras model creation successful")
        
        return True
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ TensorFlow functionality test failed: {e}")
        return False


def identify_problematic_packages():
    """Try to identify packages that might have Python 3.12 issues."""
    print("\n🔍 Identifying potentially problematic packages...")
    
    # Common packages known to have Python 3.12 issues
    potentially_problematic = [
        "setuptools",
        "pkg_resources",
        "distutils",
        "imp",
    ]
    
    issues_found = []
    
    for package in potentially_problematic:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"⚠️ {package}: {version} (may have Python 3.12 issues)")
            
            # Check for specific deprecated features
            if package == "pkg_resources":
                if hasattr(module, 'ImpImporter'):
                    print(f"   ❌ {package} uses deprecated ImpImporter")
                    issues_found.append(package)
            
        except ImportError:
            print(f"✅ {package}: Not available (good for Python 3.12)")
        except Exception as e:
            print(f"❌ {package}: Error - {e}")
            issues_found.append(package)
    
    if issues_found:
        print(f"\n⚠️ Packages with potential Python 3.12 issues: {', '.join(issues_found)}")
    else:
        print("\n✅ No obvious Python 3.12 compatibility issues found")
    
    return len(issues_found) == 0


def main():
    """Run Python 3.12 compatibility tests."""
    print("🚀 Python 3.12 Compatibility Test")
    print("=" * 50)
    
    is_python312 = check_python_version()
    
    tests = [
        ("pkgutil Compatibility", test_pkgutil_compatibility),
        ("Common Dependencies", test_common_dependencies),
        ("TensorFlow Compatibility", test_tensorflow_compatibility),
        ("Problematic Packages", identify_problematic_packages),
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
    
    print("\n" + "=" * 50)
    print(f"📊 PYTHON 3.12 COMPATIBILITY TEST RESULTS: {passed}/{total} tests passed")
    
    if is_python312:
        if passed == total:
            print("🎉 ALL TESTS PASSED - Python 3.12 compatibility looks good!")
            return 0
        else:
            print("❌ SOME TESTS FAILED - Python 3.12 compatibility issues detected")
            print("\n💡 Recommendations:")
            print("1. Update problematic packages to newer versions")
            print("2. Consider using Python 3.10 or 3.11 temporarily")
            print("3. Check for package updates that support Python 3.12")
            return 1
    else:
        print("✅ Python version < 3.12 - compatibility issues less likely")
        return 0 if passed >= total * 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
