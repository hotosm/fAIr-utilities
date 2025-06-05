#!/usr/bin/env python3
"""
Compatibility fix for efficientnet library with modern Keras versions.

This script patches the efficientnet library to work with modern Keras
where keras.utils.generic_utils has been deprecated.
"""

import sys
import importlib


def patch_keras_generic_utils():
    """Patch keras.utils.generic_utils for efficientnet compatibility."""
    print("🔧 Applying keras.utils.generic_utils compatibility patch...")
    
    try:
        import keras.utils
        
        # Check if generic_utils already exists
        if hasattr(keras.utils, 'generic_utils'):
            print("✅ keras.utils.generic_utils already available")
            return True
        
        # Create a mock generic_utils module
        class MockGenericUtils:
            @staticmethod
            def get_custom_objects():
                """Redirect to modern keras.utils.get_custom_objects()."""
                try:
                    from keras.utils import get_custom_objects
                    return get_custom_objects()
                except ImportError:
                    # Fallback to tensorflow.keras
                    import tensorflow as tf
                    return tf.keras.utils.get_custom_objects()
        
        # Monkey patch the generic_utils
        keras.utils.generic_utils = MockGenericUtils()
        print("✅ keras.utils.generic_utils compatibility patch applied")
        return True
        
    except ImportError:
        print("⚠️ keras not available for patching")
        return False
    except Exception as e:
        print(f"❌ Failed to patch keras.utils.generic_utils: {e}")
        return False


def patch_tensorflow_keras_generic_utils():
    """Patch tensorflow.keras.utils.generic_utils for efficientnet compatibility."""
    print("🔧 Applying tf.keras.utils.generic_utils compatibility patch...")
    
    try:
        import tensorflow as tf
        
        # Check if generic_utils already exists
        if hasattr(tf.keras.utils, 'generic_utils'):
            print("✅ tf.keras.utils.generic_utils already available")
            return True
        
        # Create a mock generic_utils module
        class MockGenericUtils:
            @staticmethod
            def get_custom_objects():
                """Redirect to tf.keras.utils.get_custom_objects()."""
                return tf.keras.utils.get_custom_objects()
        
        # Monkey patch the generic_utils
        tf.keras.utils.generic_utils = MockGenericUtils()
        print("✅ tf.keras.utils.generic_utils compatibility patch applied")
        return True
        
    except ImportError:
        print("⚠️ tensorflow not available for patching")
        return False
    except Exception as e:
        print(f"❌ Failed to patch tf.keras.utils.generic_utils: {e}")
        return False


def test_efficientnet_after_patch():
    """Test efficientnet functionality after applying patches."""
    print("🧪 Testing efficientnet after compatibility patches...")
    
    try:
        import efficientnet
        print("✅ efficientnet imported successfully")
        
        # Test the problematic function
        try:
            efficientnet.init_keras_custom_objects()
            print("✅ efficientnet.init_keras_custom_objects() successful")
            return True
        except Exception as e:
            print(f"❌ efficientnet.init_keras_custom_objects() failed: {e}")
            return False
            
    except ImportError:
        print("⚠️ efficientnet not available for testing")
        return False
    except Exception as e:
        print(f"❌ efficientnet test failed: {e}")
        return False


def apply_all_patches():
    """Apply all necessary compatibility patches."""
    print("🚀 Applying EfficientNet compatibility patches...")
    print("=" * 60)
    
    patches_applied = 0
    
    # Apply keras patch
    if patch_keras_generic_utils():
        patches_applied += 1
    
    # Apply tensorflow.keras patch
    if patch_tensorflow_keras_generic_utils():
        patches_applied += 1
    
    print(f"\n📊 Applied {patches_applied} compatibility patches")
    
    # Test efficientnet after patches
    if test_efficientnet_after_patch():
        print("🎉 EfficientNet compatibility patches successful!")
        return True
    else:
        print("❌ EfficientNet still has compatibility issues")
        return False


def install_compatible_efficientnet():
    """Install a compatible version of efficientnet."""
    print("📦 Installing compatible efficientnet version...")
    
    import subprocess
    
    # Try different installation strategies
    strategies = [
        "pip install 'efficientnet<2.0.0' --no-cache-dir",
        "pip install 'efficientnet==1.1.1' --no-cache-dir",
        "pip install 'keras-efficientnet-v2' --no-cache-dir",
    ]
    
    for strategy in strategies:
        try:
            print(f"🔍 Trying: {strategy}")
            result = subprocess.run(strategy.split(), capture_output=True, text=True, check=True)
            print(f"✅ Installation successful: {strategy}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Installation failed: {strategy}")
            continue
    
    print("❌ All installation strategies failed")
    return False


def main():
    """Main function to fix efficientnet compatibility."""
    print("🔧 EfficientNet Compatibility Fix")
    print("=" * 50)
    
    # First, try to apply patches to existing installation
    if apply_all_patches():
        print("\n✅ Compatibility patches applied successfully")
        return 0
    
    # If patches don't work, try installing compatible version
    print("\n🔄 Patches didn't work, trying compatible installation...")
    if install_compatible_efficientnet():
        # Try patches again after installation
        if apply_all_patches():
            print("\n✅ Compatible installation and patches successful")
            return 0
    
    print("\n⚠️ Could not resolve efficientnet compatibility")
    print("💡 Recommendations:")
    print("1. Use tf.keras.applications.EfficientNetB0 instead")
    print("2. Install keras-efficientnet-v2 as alternative")
    print("3. Pin keras and efficientnet versions in requirements")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
