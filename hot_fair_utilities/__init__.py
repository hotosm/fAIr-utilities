"""
fAIr-utilities: Comprehensive AI-assisted mapping utilities.

This package provides a unified interface to fairpredictor and geoml-toolkits
packages, along with additional utilities for AI-assisted mapping workflows.
"""

# Core functionality (existing fAIr-utilities)
from .georeferencing import georeference
from .inference import evaluate, predict
from .postprocessing import polygonize, vectorize
from .preprocessing import preprocess, yolo_v8_v1

# Training functionality (existing fAIr-utilities)
from .training import ramp_train, yolo_v8_v1_train, yolo_v8_v2_train

# Utility functions (existing fAIr-utilities)
from .utils import bbox2tiles, tms2img

# Import from fairpredictor package
try:
    from fairpredictor import (
        predict_with_tiles,
        download_model,
        validate_model,
        ModelManager,
        PredictionPipeline
    )
    FAIRPREDICTOR_AVAILABLE = True
except ImportError:
    FAIRPREDICTOR_AVAILABLE = False
    # Provide informative stub functions
    def predict_with_tiles(*args, **kwargs):
        raise ImportError(
            "fairpredictor package is required for this functionality. "
            "Install with: pip install fairpredictor"
        )

    def download_model(*args, **kwargs):
        raise ImportError(
            "fairpredictor package is required for this functionality. "
            "Install with: pip install fairpredictor"
        )

    def validate_model(*args, **kwargs):
        raise ImportError(
            "fairpredictor package is required for this functionality. "
            "Install with: pip install fairpredictor"
        )

    ModelManager = None
    PredictionPipeline = None

# Import from geoml-toolkits package
try:
    from geoml_toolkits import (
        download_tiles,
        download_osm_data,
        VectorizeMasks,
        orthogonalize_gdf,
        TileDownloader,
        OSMDataDownloader
    )
    GEOML_TOOLKITS_AVAILABLE = True
except ImportError:
    GEOML_TOOLKITS_AVAILABLE = False
    # Provide informative stub functions
    def download_tiles(*args, **kwargs):
        raise ImportError(
            "geoml-toolkits package is required for this functionality. "
            "Install with: pip install geoml-toolkits"
        )

    def download_osm_data(*args, **kwargs):
        raise ImportError(
            "geoml-toolkits package is required for this functionality. "
            "Install with: pip install geoml-toolkits"
        )

    def orthogonalize_gdf(*args, **kwargs):
        raise ImportError(
            "geoml-toolkits package is required for this functionality. "
            "Install with: pip install geoml-toolkits"
        )

    VectorizeMasks = None
    TileDownloader = None
    OSMDataDownloader = None

# Configuration and monitoring (fAIr-utilities specific)
from .config import (
    config,
    DEFAULT_OAM_TMS_MOSAIC,
    DEFAULT_YOLO_MODEL_V1,
    DEFAULT_RAMP_MODEL,
    DEFAULT_YOLO_MODEL_V2,
)
from .monitoring import logger, performance_monitor, ProgressTracker

# Validation utilities (fAIr-utilities specific)
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

# Package metadata - Dynamic based on available packages
_base_exports = [
    # Core fAIr-utilities functions
    "georeference",
    "evaluate",
    "predict",
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

    # Configuration and monitoring (fAIr-utilities specific)
    "config",
    "DEFAULT_OAM_TMS_MOSAIC",
    "DEFAULT_RAMP_MODEL",
    "DEFAULT_YOLO_MODEL_V1",
    "DEFAULT_YOLO_MODEL_V2",
    "logger",
    "performance_monitor",
    "ProgressTracker",

    # Validation utilities (fAIr-utilities specific)
    "ValidationError",
    "SecurityError",
    "validate_bbox",
    "validate_zoom_level",
    "validate_confidence",
    "validate_area_threshold",

    # Package availability flags
    "FAIRPREDICTOR_AVAILABLE",
    "GEOML_TOOLKITS_AVAILABLE",
]

# Add fairpredictor exports if available
_fairpredictor_exports = []
if FAIRPREDICTOR_AVAILABLE:
    _fairpredictor_exports = [
        "predict_with_tiles",
        "download_model",
        "validate_model",
        "ModelManager",
        "PredictionPipeline"
    ]

# Add geoml-toolkits exports if available
_geoml_exports = []
if GEOML_TOOLKITS_AVAILABLE:
    _geoml_exports = [
        "download_tiles",
        "download_osm_data",
        "VectorizeMasks",
        "orthogonalize_gdf",
        "TileDownloader",
        "OSMDataDownloader"
    ]

# Combine all available exports
__all__ = _base_exports + _fairpredictor_exports + _geoml_exports
