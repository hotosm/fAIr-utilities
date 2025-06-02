# hot_fair_utilities ( Utilities for AI Assisted Mapping fAIr )

🚀 **Now with package-based architecture using fairpredictor and geoml-toolkits!**

A comprehensive Python library for AI-assisted mapping workflows that provides a unified interface to specialized packages, eliminating code duplication while offering end-to-end capabilities from data acquisition to model prediction and advanced vectorization.

Initially developed during Open AI Challenge with [Omdeena](https://omdena.com/). We frequently do AI challenges with community!

## 🏗️ New Package-Based Architecture

Instead of duplicating code, fAIr-utilities now uses specialized packages directly:

- **`fairpredictor`**: Advanced prediction pipelines and model management
- **`geoml-toolkits`**: Data acquisition and vectorization tools
- **`fAIr-utilities`**: Core training, inference, and integration layer

## ✨ Features Available Through Package Integration

- **🌍 Data Acquisition** (from geoml-toolkits): Async tile downloading with multiple schemes
- **🏗️ OSM Integration** (from geoml-toolkits): Direct OSM data downloading via HOT Raw Data API
- **🎯 End-to-End Prediction** (from fairpredictor): Complete pipeline from tiles to predictions
- **🔧 Advanced Vectorization** (from geoml-toolkits): Potrace and rasterio-based vectorization
- **📐 Orthogonalization** (from geoml-toolkits): Automatic building footprint regularization
- **🔗 Dependency Resolution**: Automatic handling of version conflicts between packages

## 🚀 Quick Start

### Simple End-to-End Prediction

```python
import asyncio
import hot_fair_utilities as fair

async def predict_buildings():
    # Define your area of interest
    bbox = [85.514668, 27.628367, 85.528875, 27.638514]

    # Run complete prediction pipeline
    predictions = await fair.predict_with_tiles(
        model_path=fair.DEFAULT_RAMP_MODEL,
        zoom_level=18,
        bbox=bbox,
        confidence=0.5,
        area_threshold=5.0,
        orthogonalize=True
    )

    print(f"Found {len(predictions['features'])} buildings!")
    return predictions

# Run the prediction
predictions = asyncio.run(predict_buildings())
```

### Download Tiles and OSM Data

```python
import asyncio
import hot_fair_utilities as fair

async def download_data():
    bbox = [85.514668, 27.628367, 85.528875, 27.638514]

    # Download aerial imagery tiles
    tiles_dir = await fair.download_tiles(
        tms=fair.DEFAULT_OAM_TMS_MOSAIC,
        zoom=18,
        bbox=bbox,
        georeference=True
    )

    # Download OSM building data
    osm_data = await fair.download_osm_data(
        bbox=bbox,
        feature_type="building",
        dump=True,
        out="osm_buildings"
    )

    return tiles_dir, osm_data

asyncio.run(download_data())
```

## 📋 Available Models

The integration provides easy access to pre-trained models:

```python
import hot_fair_utilities as fair

# Pre-trained models
fair.DEFAULT_RAMP_MODEL          # TensorFlow Lite RAMP model
fair.DEFAULT_YOLO_MODEL_V1       # YOLO v8 segmentation model v1
fair.DEFAULT_YOLO_MODEL_V2       # YOLO v8 segmentation model v2
fair.DEFAULT_OAM_TMS_MOSAIC      # Default OAM tile service
```

## 🏗️ Architecture

### Modular Design for Easy Integration

```
hot_fair_utilities/
├── data_acquisition/          # Tile and OSM data downloading
├── vectorization/            # Advanced vectorization & regularization
├── inference/                # Enhanced prediction pipeline
├── preprocessing/            # Data preprocessing
├── postprocessing/          # Result postprocessing
└── training/                # Model training utilities
```

### Adding New Models

```python
# 1. Define your model
MY_CUSTOM_MODEL = "https://my-domain.com/model.pt"

# 2. Use with the prediction pipeline
predictions = await fair.predict_with_tiles(
    model_path=MY_CUSTOM_MODEL,
    zoom_level=18,
    bbox=my_bbox
)

# 3. The framework handles everything else!
```

## 📚 Documentation

- **[Integration Guide](INTEGRATION_GUIDE.md)** - Comprehensive guide to new features
- **[Migration Helper](migration_helper.py)** - Tool to migrate from old API
- **[Examples](examples/)** - Complete workflow examples

## 🔄 Migration from Old API

If you're upgrading from the old fAIr-utilities API:

```bash
# Run the migration helper
python migration_helper.py
```

**Old way:**

```python
from hot_fair_utilities import bbox2tiles, predict, polygonize

# Multiple manual steps...
tiles = bbox2tiles(bbox, zoom)
# ... manual downloading ...
predict(model, input_path, output_path)
polygonize(prediction_path, geojson_path)
```

**New way:**

```python
import hot_fair_utilities as fair

# Single integrated function
predictions = await fair.predict_with_tiles(
    model_path=fair.DEFAULT_RAMP_MODEL,
    zoom_level=18,
    bbox=bbox
)
```

## Prerequisites

- Python 3.8+
- GDAL (for geospatial operations)
- Optional: Potrace (for advanced vectorization)

## `hot_fair_utilities` Installation

Installing all libraries could be pain so we suggest you to use docker , If you like to do it bare , You can follow `.github/build.yml`

<!-- comment -->

Clone repo

```
git clone https://github.com/hotosm/fAIr-utilities.git
```

Navigate to fAIr-utilities:

```
cd fAIr-utilities
```

Build Docker

```
docker build --tag fairutils .
```

Run Container with default Jupyter Notebook , Or add `bash` at end to see terminal

```
docker run -it --rm --gpus=all  -p 8888:8888 fairutils
```

[Optional] If you have downloaded RAMP already , By Default tf is set as Ramp_Home , You can change that by attaching your ramp-home volume to container as tf

if not you can skip this step , Ramp code will be downloaded on package_test.ipynb

```
-v /home/hotosm/fAIr-utilities:/tf
```

## Test inside Docker Container

```
docker run -it --rm --gpus=all  -p 8888:8888 fairutils bash
```

```
python test_app.py
```

## Test Installation and workflow

You can run [`package_test.ipynb`](./Package_Test.ipynb) on your notebook from docker to test the installation and workflow with sample data provided , Or open with [collab and connect your runtime locally](https://research.google.com/colaboratory/local-runtimes.html#:~:text=In%20Colab%2C%20click%20the%20%22Connect,connected%20to%20your%20local%20runtime.)

## Get started with development

Now you can play with your data , use your own data , use different models for testing and also Help me Improve me !

### Version Control

Follow [Version Control Docs](./docs/Version_control.md) to publish and maintain new version

master --- > Dev
Releases ---- > Production
