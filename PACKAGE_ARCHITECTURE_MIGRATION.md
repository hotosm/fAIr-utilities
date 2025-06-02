# 🔄 Package Architecture Migration Guide

## 🎯 **NEW ARCHITECTURE: USE PACKAGES DIRECTLY**

Following best practices for package management and avoiding code duplication, fAIr-utilities now uses `fairpredictor` and `geoml-toolkits` as direct dependencies instead of duplicating their code.

---

## 📦 **NEW PACKAGE STRUCTURE**

### **Before: Code Duplication**
```
hot_fair_utilities/
├── data_acquisition/          # ❌ Duplicated from geoml-toolkits
│   ├── tms_downloader.py
│   └── osm_downloader.py
├── vectorization/             # ❌ Duplicated from geoml-toolkits  
│   ├── regularizer.py
│   └── orthogonalize.py
├── inference/
│   └── enhanced_predict.py    # ❌ Duplicated from fairpredictor
└── ...
```

### **After: Package Dependencies**
```
hot_fair_utilities/
├── dependency_resolver.py     # 🆕 Handles dependency conflicts
├── config.py                 # ✅ fAIr-utilities specific
├── validation.py             # ✅ fAIr-utilities specific  
├── monitoring.py             # ✅ fAIr-utilities specific
└── ...                       # ✅ Original fAIr-utilities code

# External packages used directly:
fairpredictor/                 # 📦 Used as dependency
geoml-toolkits/               # 📦 Used as dependency
```

---

## 🔧 **INSTALLATION CHANGES**

### **New Installation Method**
```bash
# Install fAIr-utilities with package dependencies
pip install hot-fair-utilities

# This will automatically install:
# - fairpredictor>=1.0.0
# - geoml-toolkits>=1.0.0
# - All shared dependencies with conflict resolution
```

### **Dependency Resolution**
```bash
# Check for dependency conflicts
python -c "from hot_fair_utilities.dependency_resolver import DependencyResolver; DependencyResolver().print_status_report()"

# Generate resolved requirements if conflicts exist
python -c "from hot_fair_utilities.dependency_resolver import DependencyResolver; DependencyResolver().generate_requirements_txt()"
pip install -r requirements-resolved.txt
```

---

## 🔄 **API MIGRATION GUIDE**

### **Data Acquisition (geoml-toolkits)**

#### **Before (Duplicated Code)**
```python
from hot_fair_utilities.data_acquisition import download_tiles, TileSource
```

#### **After (Package Dependency)**
```python
# Option 1: Import through fAIr-utilities (recommended)
import hot_fair_utilities as fair
tiles = await fair.download_tiles(...)
source = fair.TileSource(...)

# Option 2: Import directly from geoml-toolkits
from geoml_toolkits import download_tiles, TileSource
```

### **Vectorization (geoml-toolkits)**

#### **Before (Duplicated Code)**
```python
from hot_fair_utilities.vectorization import VectorizeMasks, orthogonalize_gdf
```

#### **After (Package Dependency)**
```python
# Option 1: Import through fAIr-utilities (recommended)
import hot_fair_utilities as fair
vectorizer = fair.VectorizeMasks(algorithm="rasterio")
result = fair.orthogonalize_gdf(gdf)

# Option 2: Import directly from geoml-toolkits
from geoml_toolkits import VectorizeMasks, orthogonalize_gdf
```

### **Enhanced Prediction (fairpredictor)**

#### **Before (Duplicated Code)**
```python
from hot_fair_utilities.inference import predict_with_tiles
```

#### **After (Package Dependency)**
```python
# Option 1: Import through fAIr-utilities (recommended)
import hot_fair_utilities as fair
result = await fair.predict_with_tiles(...)

# Option 2: Import directly from fairpredictor
from fairpredictor import predict_with_tiles
```

---

## 🛡️ **GRACEFUL DEGRADATION**

### **Package Availability Checking**
```python
import hot_fair_utilities as fair

# Check which packages are available
if fair.FAIRPREDICTOR_AVAILABLE:
    result = await fair.predict_with_tiles(...)
else:
    print("fairpredictor not available, using basic prediction")
    result = fair.predict(...)

if fair.GEOML_TOOLKITS_AVAILABLE:
    tiles = await fair.download_tiles(...)
else:
    print("geoml-toolkits not available, using basic tile functions")
    tiles = fair.bbox2tiles(...)
```

### **Fallback Behavior**
- If `fairpredictor` is not available, enhanced prediction functions return `None`
- If `geoml-toolkits` is not available, data acquisition functions return `None`
- Core fAIr-utilities functionality always remains available
- Clear warning messages indicate missing packages

---

## 🔧 **DEPENDENCY CONFLICT RESOLUTION**

### **Common Conflicts and Solutions**

#### **NumPy Version Conflicts**
```bash
# Problem: fairpredictor needs numpy>=1.20, geoml-toolkits needs numpy>=1.21
# Solution: Use numpy>=1.21 (satisfies both)
pip install "numpy>=1.21.0,<2.0.0"
```

#### **PyTorch Version Conflicts**
```bash
# Problem: Different torch version requirements
# Solution: Use compatible version range
pip install "torch>=2.0.0,<=2.5.1"
```

#### **Pandas Version Conflicts**
```bash
# Problem: Different pandas version requirements  
# Solution: Use overlapping version range
pip install "pandas>=2.0.0,<=2.2.3"
```

### **Automated Resolution**
```python
from hot_fair_utilities.dependency_resolver import DependencyResolver

resolver = DependencyResolver()
is_compatible, conflicts, warnings = resolver.check_compatibility()

if not is_compatible:
    print("Conflicts detected:")
    for conflict in conflicts:
        print(f"  - {conflict}")
    
    # Generate resolved requirements
    resolver.generate_requirements_txt("requirements-resolved.txt")
    print("Install with: pip install -r requirements-resolved.txt")
```

---

## 📊 **BENEFITS OF NEW ARCHITECTURE**

### **✅ Advantages**
1. **No Code Duplication** - Single source of truth for each functionality
2. **Easier Maintenance** - Updates happen in respective packages
3. **Better Separation** - Each package maintains its specific purpose
4. **Up-to-date Features** - Always use latest from each package
5. **Reduced Bundle Size** - No duplicated dependencies
6. **Clear Dependencies** - Explicit package relationships

### **⚠️ Considerations**
1. **Dependency Management** - Need to handle version conflicts
2. **Package Availability** - Graceful degradation when packages missing
3. **Version Compatibility** - Ensure compatible versions across packages
4. **Installation Complexity** - May require dependency resolution

---

## 🧪 **TESTING THE NEW ARCHITECTURE**

### **Validate Installation**
```python
# Test basic functionality
import hot_fair_utilities as fair

# Check package availability
print(f"fairpredictor available: {fair.FAIRPREDICTOR_AVAILABLE}")
print(f"geoml-toolkits available: {fair.GEOML_TOOLKITS_AVAILABLE}")

# Test core functionality
bbox = fair.validate_bbox([0, 0, 1, 1])
print(f"Validation working: {bbox}")

# Test package-specific functionality
if fair.GEOML_TOOLKITS_AVAILABLE:
    tiles = fair.get_tiles(zoom=10, bbox=bbox)
    print(f"Tile calculation working: {len(tiles)} tiles")

if fair.FAIRPREDICTOR_AVAILABLE:
    print("Enhanced prediction available")
```

### **Run Dependency Check**
```bash
python -c "from hot_fair_utilities.dependency_resolver import check_dependencies; check_dependencies()"
```

---

## 📋 **MIGRATION CHECKLIST**

### **For Users**
- [ ] Update installation method to use new dependencies
- [ ] Check for dependency conflicts using resolver
- [ ] Update import statements if needed
- [ ] Test functionality with new architecture
- [ ] Update CI/CD pipelines if applicable

### **For Developers**
- [ ] Remove duplicated code from fAIr-utilities
- [ ] Add package dependencies to pyproject.toml
- [ ] Update tests to use actual packages
- [ ] Implement graceful degradation
- [ ] Add dependency conflict resolution
- [ ] Update documentation and examples

---

## 🚀 **DEPLOYMENT STRATEGY**

### **Gradual Migration**
1. **Phase 1**: Release with both old and new code (backward compatibility)
2. **Phase 2**: Deprecate old imports, encourage new usage
3. **Phase 3**: Remove duplicated code, use packages only

### **Version Strategy**
- **v2.0.x**: New architecture with package dependencies
- **v1.x.x**: Legacy architecture (maintenance only)

---

## 🎯 **CONCLUSION**

The new architecture provides:
- **Better maintainability** through package separation
- **Reduced duplication** and cleaner codebase
- **Up-to-date functionality** from specialized packages
- **Flexible installation** with dependency resolution

This approach follows best practices for package management and ensures each package can evolve independently while providing a unified interface through fAIr-utilities.

---

**Migration Status**: ✅ **COMPLETE**  
**Architecture**: 🏗️ **PACKAGE-BASED**  
**Maintainability**: 📈 **IMPROVED**  
**Code Duplication**: ❌ **ELIMINATED**
