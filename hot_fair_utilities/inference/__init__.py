from .predict import predict
from .evaluate import evaluate

# Import enhanced prediction functionality from fairpredictor package
try:
    from fairpredictor import (
        predict_with_tiles,
        run_prediction,
        download_or_validate_model,
    )
    FAIRPREDICTOR_AVAILABLE = True
except ImportError:
    # Provide fallback functions if fairpredictor is not available
    def predict_with_tiles(*args, **kwargs):
        raise ImportError("fairpredictor package is required for predict_with_tiles functionality")

    def run_prediction(*args, **kwargs):
        raise ImportError("fairpredictor package is required for run_prediction functionality")

    def download_or_validate_model(*args, **kwargs):
        raise ImportError("fairpredictor package is required for download_or_validate_model functionality")

    FAIRPREDICTOR_AVAILABLE = False

# Import constants from config
from ..config import (
    DEFAULT_OAM_TMS_MOSAIC,
    DEFAULT_YOLO_MODEL_V1,
    DEFAULT_RAMP_MODEL,
    DEFAULT_YOLO_MODEL_V2,
)
