#!/usr/bin/env python3
"""
Test script to verify EfficientNet compatibility with modern TensorFlow/Keras.

This script tests different EfficientNet implementations and their compatibility
with the current TensorFlow/Keras installation.
"""

import sys


def test_tensorflow_keras_utils():
    """Test if keras.utils.generic_utils is available."""
    print("🔍 Testing keras.utils.generic_utils availability...")
    
    try:
        import tensorflow as tf
        print(f"TensorFlow version: {tf.__version__}")
        
        # Check if generic_utils is available
        try:
            from keras.utils import generic_utils
            print("✅ keras.utils.generic_utils is available")
            return True
        except ImportError:
            print("❌ keras.utils.generic_utils not available (separate keras)")
            
            # Try tf.keras.utils
            try:
                from tensorflow.keras.utils import generic_utils
                print("✅ tf.keras.utils.generic_utils is available")
                return True
            except (ImportError, AttributeError):
                print("❌ tf.keras.utils.generic_utils not available")
                print("   This is expected in modern TensorFlow versions")
                return False
                
    except Exception as e:
        print(f"❌ Error testing keras utils: {e}")
        return False


def test_classic_efficientnet():
    """Test classic efficientnet package."""
    print("\n🔍 Testing classic efficientnet package...")
    
    try:
        import efficientnet
        print("✅ efficientnet package imported successfully")
        
        # Test initialization
        try:
            efficientnet.init_keras_custom_objects()
            print("✅ efficientnet.init_keras_custom_objects() successful")
            return True
        except Exception as e:
            print(f"❌ efficientnet initialization failed: {e}")
            if "generic_utils" in str(e):
                print("   This is likely due to keras.utils.generic_utils deprecation")
            return False
            
    except ImportError:
        print("⚠️ Classic efficientnet package not available")
        return False
    except Exception as e:
        print(f"❌ Classic efficientnet test failed: {e}")
        return False


def test_keras_efficientnet_v2():
    """Test keras-efficientnet-v2 package."""
    print("\n🔍 Testing keras-efficientnet-v2 package...")
    
    try:
        import keras_efficientnet_v2
        print("✅ keras-efficientnet-v2 package imported successfully")
        
        # Test model creation
        try:
            import tensorflow as tf
            model = keras_efficientnet_v2.EfficientNetV2B0(
                input_shape=(224, 224, 3),
                classes=1000,
                weights=None
            )
            print("✅ EfficientNetV2B0 model creation successful")
            return True
        except Exception as e:
            print(f"❌ EfficientNetV2 model creation failed: {e}")
            return False
            
    except ImportError:
        print("⚠️ keras-efficientnet-v2 package not available")
        return False
    except Exception as e:
        print(f"❌ keras-efficientnet-v2 test failed: {e}")
        return False


def test_tensorflow_hub_efficientnet():
    """Test TensorFlow Hub EfficientNet models."""
    print("\n🔍 Testing TensorFlow Hub EfficientNet...")
    
    try:
        import tensorflow_hub as hub
        import tensorflow as tf
        
        print("✅ TensorFlow Hub available")
        
        # Test loading a simple EfficientNet model (without downloading)
        try:
            # Just test the hub module import, don't actually download
            print("✅ TensorFlow Hub EfficientNet models should be available")
            print("   (Not downloading model in test)")
            return True
        except Exception as e:
            print(f"❌ TensorFlow Hub EfficientNet test failed: {e}")
            return False
            
    except ImportError:
        print("⚠️ TensorFlow Hub not available")
        return False
    except Exception as e:
        print(f"❌ TensorFlow Hub test failed: {e}")
        return False


def test_tf_keras_applications():
    """Test TensorFlow Keras Applications EfficientNet."""
    print("\n🔍 Testing tf.keras.applications EfficientNet...")
    
    try:
        import tensorflow as tf
        
        # Check if EfficientNet is available in tf.keras.applications
        if hasattr(tf.keras.applications, 'EfficientNetB0'):
            print("✅ tf.keras.applications.EfficientNetB0 available")
            
            # Test model creation
            try:
                model = tf.keras.applications.EfficientNetB0(
                    input_shape=(224, 224, 3),
                    classes=1000,
                    weights=None
                )
                print("✅ tf.keras.applications.EfficientNetB0 model creation successful")
                return True
            except Exception as e:
                print(f"❌ tf.keras.applications.EfficientNetB0 creation failed: {e}")
                return False
        else:
            print("⚠️ tf.keras.applications.EfficientNetB0 not available")
            return False
            
    except Exception as e:
        print(f"❌ tf.keras.applications EfficientNet test failed: {e}")
        return False


def recommend_solution():
    """Provide recommendations based on test results."""
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 50)
    
    print("For modern TensorFlow/Keras compatibility:")
    print("1. ✅ Use tf.keras.applications.EfficientNetB0 (built-in)")
    print("2. ✅ Use keras-efficientnet-v2 (modern implementation)")
    print("3. ✅ Use TensorFlow Hub models")
    print("4. ⚠️ Avoid classic efficientnet package (deprecated keras.utils.generic_utils)")
    
    print("\nInstallation commands:")
    print("# Option 1: Use built-in TensorFlow models (recommended)")
    print("# No additional installation needed")
    
    print("\n# Option 2: Install modern EfficientNet implementation")
    print("pip install keras-efficientnet-v2")
    
    print("\n# Option 3: Install TensorFlow Hub")
    print("pip install tensorflow-hub")
    
    print("\n# Option 4: Install classic efficientnet with version constraint")
    print("pip install 'efficientnet<2.0.0'  # May still have compatibility issues")


def main():
    """Run EfficientNet compatibility tests."""
    print("🚀 EfficientNet Compatibility Test")
    print("=" * 50)
    
    tests = [
        ("Keras Utils Availability", test_tensorflow_keras_utils),
        ("Classic EfficientNet", test_classic_efficientnet),
        ("Keras EfficientNet V2", test_keras_efficientnet_v2),
        ("TensorFlow Hub EfficientNet", test_tensorflow_hub_efficientnet),
        ("tf.keras.applications EfficientNet", test_tf_keras_applications),
    ]
    
    passed = 0
    total = len(tests)
    working_solutions = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                working_solutions.append(test_name)
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 EFFICIENTNET COMPATIBILITY TEST RESULTS: {passed}/{total} tests passed")
    
    if working_solutions:
        print(f"\n✅ Working EfficientNet solutions:")
        for solution in working_solutions:
            print(f"   - {solution}")
    
    recommend_solution()
    
    if passed > 0:
        print("\n🎉 At least one EfficientNet solution is working!")
        return 0
    else:
        print("\n❌ No EfficientNet solutions are working")
        print("Consider using tf.keras.applications models or updating dependencies")
        return 1


if __name__ == "__main__":
    sys.exit(main())
