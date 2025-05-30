# fAIr-utilities Integration Guide

This guide explains the newly integrated functionality from `geoml-toolkits` and `fairpredictor` into the main `fAIr-utilities` repository.

## 🎯 What's New

### Integrated Modules

1. **Data Acquisition** (`hot_fair_utilities.data_acquisition`)
   - Async TMS tile downloading with multiple schemes support
   - OSM data downloading via HOT Raw Data API
   - Support for XYZ, TMS, QuadKey, and custom tile schemes
   - Automatic georeferencing and CRS transformations

2. **Advanced Vectorization** (`hot_fair_utilities.vectorization`)
   - Potrace-based vectorization for smooth curves
   - Rasterio-based vectorization for direct conversion
   - Geometry regularization and orthogonalization
   - Advanced polygon cleaning and simplification

3. **Enhanced Prediction** (`hot_fair_utilities.inference`)
   - End-to-end prediction pipeline
   - Automatic model downloading
   - Integrated tile downloading and vectorization
   - Support for multiple model formats

## 🚀 Quick Start

### Basic End-to-End Prediction

```python
import asyncio
import hot_fair_utilities as fair

async def predict_buildings():
    # Define area of interest
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

### Download Tiles Only

```python
import asyncio
import hot_fair_utilities as fair

async def download_imagery():
    tiles_dir = await fair.download_tiles(
        tms=fair.DEFAULT_OAM_TMS_MOSAIC,
        zoom=18,
        bbox=[85.514668, 27.628367, 85.528875, 27.638514],
        out="my_tiles",
        georeference=True,
        crs="3857"
    )
    print(f"Tiles saved to: {tiles_dir}")

asyncio.run(download_imagery())
```

### Download OSM Data

```python
import asyncio
import hot_fair_utilities as fair

async def download_buildings():
    osm_data = await fair.download_osm_data(
        bbox=[85.514668, 27.628367, 85.528875, 27.638514],
        feature_type="building",
        dump=True,
        out="osm_buildings"
    )
    print(f"OSM data saved to: {osm_data}")

asyncio.run(download_buildings())
```

### Advanced Vectorization

```python
import hot_fair_utilities as fair

# Create vectorizer with custom settings
converter = fair.VectorizeMasks(
    simplify_tolerance=0.2,
    min_area=5.0,
    orthogonalize=True,
    algorithm="potrace"  # or "rasterio"
)

# Convert mask to vector
gdf = converter.convert("prediction_mask.tif", "buildings.geojson")
print(f"Vectorized {len(gdf)} buildings")
```

## 🔧 Available Models

The integration provides easy access to pre-trained models:

```python
import hot_fair_utilities as fair

# Available models
fair.DEFAULT_RAMP_MODEL          # TensorFlow Lite RAMP model
fair.DEFAULT_YOLO_MODEL_V1       # YOLO v8 segmentation model v1
fair.DEFAULT_YOLO_MODEL_V2       # YOLO v8 segmentation model v2
fair.DEFAULT_OAM_TMS_MOSAIC      # Default OAM tile service
```

## 🏗️ Architecture

### Modular Design

The new architecture is designed for easy model integration:

```
hot_fair_utilities/
├── data_acquisition/          # Tile and OSM data downloading
│   ├── tms_downloader.py     # TMS tile downloading
│   └── osm_downloader.py     # OSM data via HOT API
├── vectorization/            # Advanced vectorization
│   ├── regularizer.py        # Main vectorization class
│   └── orthogonalize.py      # Geometry regularization
├── inference/                # Enhanced prediction
│   ├── predict.py           # Basic prediction
│   └── enhanced_predict.py  # End-to-end pipeline
└── ...
```

### Easy Model Integration

To integrate a new model:

1. **Add your model URL or path**:
```python
MY_CUSTOM_MODEL = "https://my-domain.com/model.pt"
```

2. **Use the prediction pipeline**:
```python
predictions = await fair.predict_with_tiles(
    model_path=MY_CUSTOM_MODEL,
    zoom_level=18,
    bbox=my_bbox,
    confidence=0.6
)
```

3. **The framework handles everything else**!

## 📊 Parameters Reference

### `predict_with_tiles()` Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | str | - | Path or URL to model file |
| `zoom_level` | int | - | Zoom level for tiles |
| `bbox` | List[float] | None | Bounding box [xmin, ymin, xmax, ymax] |
| `geojson` | str/dict | None | GeoJSON for area of interest |
| `confidence` | float | 0.5 | Prediction confidence threshold |
| `area_threshold` | float | 3.0 | Minimum polygon area (sq meters) |
| `tolerance` | float | 0.5 | Simplification tolerance (meters) |
| `orthogonalize` | bool | True | Apply orthogonalization |
| `vectorization_algorithm` | str | "rasterio" | "potrace" or "rasterio" |
| `crs` | str | "3857" | Coordinate reference system |

### `VectorizeMasks` Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `simplify_tolerance` | float | 0.2 | Geometry simplification tolerance |
| `min_area` | float | 1.0 | Minimum area threshold (sq meters) |
| `orthogonalize` | bool | True | Apply orthogonalization |
| `algorithm` | str | "potrace" | "potrace" or "rasterio" |

## 🔄 Migration from Old Code

### Old Workflow
```python
# Old way - multiple steps, manual coordination
from hot_fair_utilities import preprocess, predict, polygonize

preprocess(input_path, output_path, ...)
predict(model_path, input_path, prediction_path, ...)
polygonize(prediction_path, geojson_path, ...)
```

### New Integrated Workflow
```python
# New way - single function, automatic coordination
import hot_fair_utilities as fair

predictions = await fair.predict_with_tiles(
    model_path=fair.DEFAULT_RAMP_MODEL,
    zoom_level=18,
    bbox=bbox
)
```

## 🧪 Testing

Run the comprehensive example:

```bash
python examples/integrated_workflow_example.py
```

## 📝 Dependencies

New dependencies added:
- `aiohttp>=3.8.0` - Async HTTP client
- `pyproj>=3.0.0` - Coordinate transformations
- `tensorflow>=2.10.0` - TensorFlow models

## 🤝 Contributing

To add new models or functionality:

1. Follow the modular architecture
2. Add appropriate type hints
3. Include comprehensive docstrings
4. Add examples to the integration guide
5. Test with the example workflow

## 📚 Examples

See `examples/integrated_workflow_example.py` for comprehensive usage examples covering:
- Complete end-to-end workflows
- Individual component usage
- Model integration patterns
- Advanced vectorization techniques
