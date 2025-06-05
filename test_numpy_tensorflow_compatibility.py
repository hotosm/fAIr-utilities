#!/usr/bin/env python3
"""
Test script to verify NumPy and TensorFlow compatibility.

This script tests that NumPy and TensorFlow versions are compatible
and can work together without import errors.
"""

import sys


def test_numpy_import():
    """Test NumPy import and version."""
    print("🔍 Testing NumPy import...")
    try:
        import numpy as np
        print(f"✅ NumPy import successful - version: {np.__version__}")
        
        # Test basic NumPy functionality
        arr = np.array([1, 2, 3, 4])
        print(f"✅ NumPy basic operations work: {arr}")
        
        return True, np.__version__
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False, None


def test_tensorflow_import():
    """Test TensorFlow import and version."""
    print("🔍 Testing TensorFlow import...")
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow import successful - version: {tf.__version__}")
        
        # Test basic TensorFlow functionality
        x = tf.constant([1, 2, 3, 4])
        print(f"✅ TensorFlow basic operations work: {x}")
        
        return True, tf.__version__
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")
        return False, None


def test_numpy_tensorflow_compatibility():
    """Test NumPy and TensorFlow working together."""
    print("🔍 Testing NumPy and TensorFlow compatibility...")
    try:
        import numpy as np
        import tensorflow as tf
        
        # Test NumPy array to TensorFlow tensor conversion
        np_array = np.array([1.0, 2.0, 3.0, 4.0])
        tf_tensor = tf.constant(np_array)
        
        print(f"✅ NumPy array: {np_array}")
        print(f"✅ TensorFlow tensor: {tf_tensor}")
        
        # Test TensorFlow tensor to NumPy array conversion
        back_to_numpy = tf_tensor.numpy()
        print(f"✅ Back to NumPy: {back_to_numpy}")
        
        # Test mathematical operations
        result = tf.reduce_sum(tf_tensor)
        print(f"✅ TensorFlow operation result: {result}")
        
        return True
    except Exception as e:
        print(f"❌ NumPy/TensorFlow compatibility test failed: {e}")
        return False


def check_version_compatibility(numpy_version, tensorflow_version):
    """Check if NumPy and TensorFlow versions are compatible."""
    print("🔍 Checking version compatibility...")
    
    # Parse versions
    try:
        numpy_major, numpy_minor = map(int, numpy_version.split('.')[:2])
        tf_major, tf_minor = map(int, tensorflow_version.split('.')[:2])
        
        print(f"NumPy version: {numpy_major}.{numpy_minor}")
        print(f"TensorFlow version: {tf_major}.{tf_minor}")
        
        # Check compatibility rules
        if tf_major == 2:
            if tf_minor >= 17:  # TensorFlow 2.17+
                if numpy_major == 1 and numpy_minor >= 26:
                    print("✅ Compatible: TensorFlow 2.17+ supports NumPy 1.26+")
                    return True
                elif numpy_major == 2:
                    print("✅ Compatible: TensorFlow 2.17+ supports NumPy 2.x")
                    return True
                else:
                    print("⚠️ Warning: NumPy version may be too old for TensorFlow 2.17+")
                    return False
            elif tf_minor >= 15:  # TensorFlow 2.15-2.16
                if numpy_major == 1 and 22 <= numpy_minor < 24:
                    print("✅ Compatible: TensorFlow 2.15-2.16 requires NumPy 1.22-1.23")
                    return True
                else:
                    print("❌ Incompatible: TensorFlow 2.15-2.16 requires NumPy >=1.22,<1.24")
                    return False
            elif tf_minor >= 12:  # TensorFlow 2.12-2.14
                if numpy_major == 1 and 22 <= numpy_minor < 24:
                    print("✅ Compatible: TensorFlow 2.12-2.14 requires NumPy 1.22-1.23")
                    return True
                else:
                    print("❌ Incompatible: TensorFlow 2.12-2.14 requires NumPy >=1.22,<1.24")
                    return False
            else:
                print("⚠️ Warning: TensorFlow version too old, compatibility unknown")
                return False
        else:
            print("⚠️ Warning: TensorFlow version not supported")
            return False
            
    except Exception as e:
        print(f"❌ Version parsing failed: {e}")
        return False


def get_python_version_info():
    """Get Python version information."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"🐍 Python version: {python_version}")
    return python_version


def main():
    """Run NumPy/TensorFlow compatibility tests."""
    print("🚀 Testing NumPy and TensorFlow Compatibility...")
    print("=" * 60)
    
    # Get Python version
    python_version = get_python_version_info()
    
    # Test NumPy
    print(f"\n{'='*20} NumPy Test {'='*20}")
    numpy_success, numpy_version = test_numpy_import()
    
    # Test TensorFlow
    print(f"\n{'='*20} TensorFlow Test {'='*20}")
    tensorflow_success, tensorflow_version = test_tensorflow_import()
    
    # Test compatibility
    if numpy_success and tensorflow_success:
        print(f"\n{'='*20} Compatibility Test {'='*20}")
        compatibility_success = test_numpy_tensorflow_compatibility()
        
        print(f"\n{'='*20} Version Compatibility {'='*20}")
        version_compatibility = check_version_compatibility(numpy_version, tensorflow_version)
    else:
        compatibility_success = False
        version_compatibility = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 NUMPY/TENSORFLOW COMPATIBILITY SUMMARY")
    print("=" * 60)
    
    print(f"Python Version: {python_version}")
    if numpy_success:
        print(f"NumPy Version: {numpy_version}")
    if tensorflow_success:
        print(f"TensorFlow Version: {tensorflow_version}")
    
    print(f"\nTest Results:")
    print(f"NumPy Import: {'✅ PASS' if numpy_success else '❌ FAIL'}")
    print(f"TensorFlow Import: {'✅ PASS' if tensorflow_success else '❌ FAIL'}")
    print(f"Compatibility Test: {'✅ PASS' if compatibility_success else '❌ FAIL'}")
    print(f"Version Compatibility: {'✅ PASS' if version_compatibility else '❌ FAIL'}")
    
    if numpy_success and tensorflow_success and compatibility_success and version_compatibility:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ NumPy and TensorFlow are compatible and working correctly")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("🔧 Check NumPy and TensorFlow versions for compatibility")
        
        # Provide troubleshooting hints
        print("\n💡 Troubleshooting hints:")
        if not numpy_success:
            print("- Install NumPy: pip install numpy")
        if not tensorflow_success:
            print("- Install TensorFlow: pip install tensorflow")
        if not version_compatibility:
            print("- Check version compatibility matrix")
            print("- For TensorFlow 2.12-2.16: use numpy>=1.22,<1.24")
            print("- For TensorFlow 2.17+: use numpy>=1.26 or numpy 2.x")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
