# 🤖 TensorFlow/Keras Compatibility Guide

## 📊 **TENSORFLOW AND KERAS INTEGRATION**

### **Modern TensorFlow (2.15+)**
- ✅ **TensorFlow includes Keras** - No separate Keras installation needed
- ✅ **Use tf.keras** - Integrated Keras API within TensorFlow
- ✅ **Automatic compatibility** - TensorFlow manages Keras version internally

### **Key Changes from Previous Versions**
- ❌ **No separate keras package** - Don't install `keras` separately
- ✅ **Use tf.keras instead** - All Keras functionality through `tf.keras`
- ✅ **Version managed by TensorFlow** - Keras version matches TensorFlow

---

## 🔧 **COMPATIBILITY MATRIX**

### **Python 3.10**
- ✅ **TensorFlow**: `>=2.15.0,<3.0.0`
- ✅ **NumPy**: `>=1.22.0,<1.24.0`
- ✅ **Keras**: Included in TensorFlow (tf.keras)

### **Python 3.11**
- ✅ **TensorFlow**: `>=2.16.0,<3.0.0`
- ✅ **NumPy**: `>=1.22.0,<1.24.0`
- ✅ **Keras**: Included in TensorFlow (tf.keras)

### **Python 3.12**
- ✅ **TensorFlow**: `>=2.17.1,<3.0.0`
- ✅ **NumPy**: `>=1.26.0,<2.0.0`
- ✅ **Keras**: Included in TensorFlow (tf.keras)

---

## ❌ **COMMON ISSUES RESOLVED**

### **Issue 1: Separate Keras Installation**
- **Problem**: Installing `keras>=2.17.1` separately (version doesn't exist)
- **Solution**: Remove separate Keras installation, use tf.keras
- **Status**: ✅ **RESOLVED**

### **Issue 2: Version Mismatch**
- **Problem**: TensorFlow 2.19.0 requires keras>=3.5.0 but keras 2.15.0 installed
- **Solution**: Don't install separate Keras, let TensorFlow manage it
- **Status**: ✅ **RESOLVED**

### **Issue 3: API AttributeError**
- **Problem**: `tf.__internal__.register_load_context_function` not found
- **Solution**: Use tf.keras instead of separate keras, avoid internal APIs
- **Status**: ✅ **RESOLVED**

---

## 🚀 **CORRECT INSTALLATION PROCESS**

### **Step 1: Install TensorFlow Only**
```bash
# Python 3.10
pip install "tensorflow>=2.15.0,<3.0.0"

# Python 3.11  
pip install "tensorflow>=2.16.0,<3.0.0"

# Python 3.12
pip install "tensorflow>=2.17.1,<3.0.0"
```

### **Step 2: Use tf.keras (NOT separate keras)**
```python
import tensorflow as tf

# ✅ Correct - Use tf.keras
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)
])

# ❌ Incorrect - Don't import separate keras
# import keras  # Don't do this
```

### **Step 3: Verify Installation**
```python
import tensorflow as tf
print(f"TensorFlow version: {tf.__version__}")
print(f"Keras version: {tf.keras.__version__}")

# Test basic functionality
model = tf.keras.Sequential([tf.keras.layers.Dense(1)])
model.compile(optimizer='adam', loss='mse')
print("✅ tf.keras working correctly")
```

---

## 🔍 **SEGMENTATION-MODELS COMPATIBILITY**

### **Correct Usage with tf.keras**
```python
import segmentation_models as sm
import tensorflow as tf

# Set framework to tf.keras (not separate keras)
sm.set_framework('tf.keras')

# Verify framework
print(f"Framework: {sm.framework()}")  # Should show 'tf.keras'

# Create model using tf.keras backend
model = sm.Unet('resnet34', classes=1, activation='sigmoid')
```

### **Common Issues Fixed**
- ✅ **Framework setting** - Use 'tf.keras' not 'keras'
- ✅ **Backend compatibility** - segmentation-models works with tf.keras
- ✅ **Model creation** - All models use tf.keras layers

---

## 📋 **WORKFLOW CONFIGURATION**

### **Correct Workflow Steps**
```yaml
- name: Install TensorFlow with Python version compatibility
  run: |
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    
    if [[ "$PYTHON_VERSION" == "3.12" ]]; then
      pip install "tensorflow>=2.17.1,<3.0.0" --no-cache-dir
    elif [[ "$PYTHON_VERSION" == "3.11" ]]; then
      pip install "tensorflow>=2.16.0,<3.0.0" --no-cache-dir
    else
      pip install "tensorflow>=2.15.0,<3.0.0" --no-cache-dir
    fi

- name: Verify TensorFlow and Keras compatibility
  run: |
    python -c "
    import tensorflow as tf
    print(f'TensorFlow: {tf.__version__}')
    print(f'tf.keras: {tf.keras.__version__}')
    model = tf.keras.Sequential([tf.keras.layers.Dense(1)])
    print('✅ tf.keras working correctly')
    "
```

### **What NOT to Do**
```yaml
# ❌ Don't install separate keras
- name: Install Keras separately
  run: pip install keras>=2.17.1  # This version doesn't exist

# ❌ Don't try to match keras version to tensorflow
- name: Install matching versions
  run: |
    pip install tensorflow==2.19.0
    pip install keras>=3.5.0  # Let TensorFlow manage this
```

---

## 🧪 **TESTING AND VERIFICATION**

### **Basic Compatibility Test**
```python
def test_tensorflow_keras():
    import tensorflow as tf
    
    # Check versions
    print(f"TensorFlow: {tf.__version__}")
    print(f"tf.keras: {tf.keras.__version__}")
    
    # Test model creation
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    
    # Test compilation
    model.compile(optimizer='adam', loss='mse')
    
    print("✅ tf.keras working correctly")
    return True
```

### **segmentation-models Test**
```python
def test_segmentation_models():
    import segmentation_models as sm
    
    # Set framework
    sm.set_framework('tf.keras')
    
    # Verify framework
    framework = sm.framework()
    assert framework == 'tf.keras'
    
    print("✅ segmentation-models with tf.keras working")
    return True
```

---

## 📝 **REQUIREMENTS FILES**

### **Correct requirements-build.txt**
```
tensorflow>=2.15.0,<3.0.0
segmentation-models>=1.0.0
# Note: No separate keras package needed
```

### **Incorrect requirements-build.txt**
```
tensorflow>=2.15.0,<3.0.0
keras>=2.17.1,<3.0.0  # ❌ Don't do this - version doesn't exist
segmentation-models>=1.0.0
```

---

## ✅ **STATUS**

**Current Status**: ✅ **FULLY COMPATIBLE**
- ✅ TensorFlow includes Keras (tf.keras)
- ✅ No separate Keras installation needed
- ✅ All Python versions (3.10, 3.11, 3.12) supported
- ✅ segmentation-models works with tf.keras backend
- ✅ All CI/CD workflows updated and working
- ✅ Version conflicts resolved

**Key Takeaway**: Modern TensorFlow (2.15+) includes Keras as tf.keras. Don't install separate keras package - use tf.keras for all Keras functionality.
