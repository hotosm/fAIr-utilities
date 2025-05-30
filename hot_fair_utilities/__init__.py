"""
fAIr-utilities: Comprehensive AI-assisted mapping utilities.

This package provides end-to-end capabilities for AI-assisted mapping workflows,
including data acquisition, model training, inference, and advanced vectorization.
"""

# Core functionality
from .georeferencing import georeference
from .inference import evaluate, predict, predict_with_tiles
from .postprocessing import polygonize, vectorize
from .preprocessing import preprocess, yolo_v8_v1

# Training functionality
from .training import ramp_train, yolo_v8_v1_train, yolo_v8_v2_train

# Utility functions
from .utils import bbox2tiles, tms2img

# New integrated modules
from .data_acquisition import download_tiles, download_osm_data
from .vectorization import VectorizeMasks, orthogonalize_gdf

# Configuration and monitoring
from .config import (
    config,
    DEFAULT_OAM_TMS_MOSAIC,
    DEFAULT_YOLO_MODEL_V1,
    DEFAULT_RAMP_MODEL,
    DEFAULT_YOLO_MODEL_V2,
)
from .monitoring import logger, performance_monitor, ProgressTracker

# Validation utilities
from .validation import (
    ValidationError,
    SecurityError,
    validate_bbox,
    validate_zoom_level,
    validate_confidence,
    validate_area_threshold,
)

# Version information
__version__ = "2.0.0"
__author__ = "HOT OSM Team"
__email__ = "tech@hotosm.org"
__description__ = "Comprehensive AI-assisted mapping utilities with integrated data acquisition and advanced vectorization"

# Package metadata
__all__ = [
    # Core functions
    "georeference",
    "evaluate",
    "predict",
    "predict_with_tiles",
    "polygonize",
    "vectorize",
    "preprocess",
    "yolo_v8_v1",

    # Training functions
    "ramp_train",
    "yolo_v8_v1_train",
    "yolo_v8_v2_train",

    # Utility functions
    "bbox2tiles",
    "tms2img",

    # Data acquisition
    "download_tiles",
    "download_osm_data",

    # Vectorization
    "VectorizeMasks",
    "orthogonalize_gdf",

    # Configuration
    "config",
    "DEFAULT_OAM_TMS_MOSAIC",
    "DEFAULT_RAMP_MODEL",
    "DEFAULT_YOLO_MODEL_V1",
    "DEFAULT_YOLO_MODEL_V2",

    # Monitoring
    "logger",
    "performance_monitor",
    "ProgressTracker",

    # Validation
    "ValidationError",
    "SecurityError",
    "validate_bbox",
    "validate_zoom_level",
    "validate_confidence",
    "validate_area_threshold",
]
