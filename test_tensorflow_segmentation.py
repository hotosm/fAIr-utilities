#!/usr/bin/env python3
"""
Test script to verify TensorFlow and segmentation-models installation.

This script tests that TensorFlow can be imported successfully
and that segmentation-models works with TensorFlow backend.
"""

import sys


def test_tensorflow_import():
    """Test TensorFlow import."""
    print("🔍 Testing TensorFlow import...")
    try:
        import tensorflow as tf
        import sys

        tf_version = tf.__version__
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        print(f"✅ TensorFlow import successful - version: {tf_version}")
        print(f"🐍 Python version: {python_version}")

        # Check version compatibility
        if python_version == "3.12" and tf_version.startswith("2.12"):
            print("⚠️ Warning: TensorFlow 2.12.x may not be fully compatible with Python 3.12")

        # Test basic TensorFlow functionality
        print("🔍 Testing basic TensorFlow functionality...")
        x = tf.constant([1, 2, 3, 4])
        print(f"✅ TensorFlow basic operations work: {x}")

        return True
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ TensorFlow functionality test failed: {e}")
        return False


def test_segmentation_models_import():
    """Test segmentation-models import with TensorFlow backend."""
    print("🔍 Testing segmentation-models import...")
    try:
        import segmentation_models as sm
        print(f"✅ segmentation-models import successful - version: {sm.__version__}")

        # Test that TensorFlow backend is working
        print("🔍 Testing segmentation-models with TensorFlow backend...")
        sm.set_framework('tf.keras')
        print("✅ TensorFlow backend (tf.keras) set successfully")

        # Test framework detection
        framework = sm.framework()
        print(f"✅ Current framework: {framework}")

        return True
    except ImportError as e:
        print(f"❌ segmentation-models import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ segmentation-models functionality test failed: {e}")
        return False


def test_tensorflow_keras():
    """Test TensorFlow Keras functionality."""
    print("🔍 Testing TensorFlow Keras...")
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow Keras (tf.keras) version: {tf.keras.__version__}")

        # Test basic Keras functionality
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(1, input_shape=(1,))
        ])
        print("✅ Basic tf.keras model creation successful")

        # Test model compilation
        model.compile(optimizer='adam', loss='mse')
        print("✅ tf.keras model compilation successful")

        return True
    except ImportError as e:
        print(f"❌ TensorFlow Keras import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ TensorFlow Keras functionality test failed: {e}")
        return False


def test_segmentation_models_functionality():
    """Test basic segmentation-models functionality."""
    print("🔍 Testing segmentation-models basic functionality...")
    try:
        import segmentation_models as sm
        
        # Test getting available models
        print("🔍 Testing available models...")
        models = ['Unet', 'FPN', 'Linknet', 'PSPNet']
        for model_name in models:
            if hasattr(sm, model_name):
                print(f"✅ {model_name} model available")
            else:
                print(f"⚠️ {model_name} model not available")
        
        return True
    except Exception as e:
        print(f"❌ segmentation-models functionality test failed: {e}")
        return False


def main():
    """Run TensorFlow and segmentation-models tests."""
    print("🚀 Testing TensorFlow and segmentation-models installation...")
    print("=" * 60)
    
    tests = [
        ("TensorFlow Import", test_tensorflow_import),
        ("TensorFlow Keras", test_tensorflow_keras),
        ("segmentation-models Import", test_segmentation_models_import),
        ("segmentation-models Functionality", test_segmentation_models_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TENSORFLOW/SEGMENTATION-MODELS TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 TENSORFLOW AND SEGMENTATION-MODELS WORKING CORRECTLY!")
        print("✅ All TensorFlow and segmentation-models functionality verified")
        return 0
    else:
        print("❌ SOME TENSORFLOW/SEGMENTATION-MODELS TESTS FAILED")
        print("🔧 Check TensorFlow installation and compatibility")
        
        # Provide troubleshooting hints
        print("\n💡 Troubleshooting hints:")
        print("1. Ensure TensorFlow is installed: pip install tensorflow")
        print("2. Ensure segmentation-models is installed: pip install segmentation-models")
        print("3. Check compatibility: TensorFlow >= 2.10.0")
        print("4. Verify installation order: TensorFlow first, then segmentation-models")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
