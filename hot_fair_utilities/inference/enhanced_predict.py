"""
Enhanced prediction module integrating fairpredictor functionality.

This module provides a streamlined prediction workflow that includes:
- Model downloading and validation
- Tile downloading from TMS sources
- Model inference
- Advanced vectorization and regularization
- End-to-end prediction pipeline
"""

import json
import logging
import os
import shutil
import time
import uuid
import urllib.request
from typing import Dict, List, Optional, Union

from ..data_acquisition import download_tiles
from ..utils import merge_rasters
from ..validation import (
    validate_bbox, validate_zoom_level, validate_confidence,
    validate_area_threshold, validate_url, validate_file_path,
    ValidationError, SecurityError
)
from ..vectorization import VectorizeMasks
from .predict import predict as basic_predict

# Set up logging
logger = logging.getLogger(__name__)


def download_or_validate_model(model_path: str, cache_dir: Optional[str] = None) -> str:
    """
    Download model if it's a URL or validate if it's a local path with comprehensive validation.

    Args:
        model_path: Path to model file or URL
        cache_dir: Directory to cache downloaded models (optional)

    Returns:
        Local path to the validated model file

    Raises:
        ValidationError: If model path is invalid
        SecurityError: If URL poses security risk
        FileNotFoundError: If local file doesn't exist
        RuntimeError: If download fails
    """
    if not isinstance(model_path, str):
        raise ValidationError(f"Model path must be a string, got {type(model_path)}")

    if not model_path.strip():
        raise ValidationError("Model path cannot be empty")

    if model_path.startswith(('http://', 'https://')):
        # Validate URL
        validated_url = validate_url(model_path)

        # Set up cache directory
        if cache_dir is None:
            cache_dir = os.path.join(os.getcwd(), ".model_cache")
        os.makedirs(cache_dir, exist_ok=True)

        # Generate safe filename
        filename = os.path.basename(validated_url.split('?')[0])  # Remove query params
        if not filename or '.' not in filename:
            filename = f"model_{hash(validated_url) % 10000}.pt"

        # Validate filename
        from ..validation import sanitize_filename
        filename = sanitize_filename(filename)
        local_path = os.path.join(cache_dir, filename)

        # Download if not exists or validate existing file
        if not os.path.exists(local_path):
            logger.info(f"Downloading model from {validated_url}")
            try:
                # Download with timeout and size limits
                import urllib.request
                import urllib.error

                # Set up request with headers and timeout
                request = urllib.request.Request(
                    validated_url,
                    headers={'User-Agent': 'fAIr-utilities/1.0'}
                )

                with urllib.request.urlopen(request, timeout=300) as response:
                    # Check content length
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        if size_mb > 5000:  # 5GB limit
                            raise RuntimeError(f"Model file too large: {size_mb:.1f}MB (max 5GB)")

                    # Download with progress
                    with open(local_path, 'wb') as f:
                        downloaded = 0
                        chunk_size = 8192
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Size check during download
                            if downloaded > 5 * 1024 * 1024 * 1024:  # 5GB
                                raise RuntimeError("Model file too large during download")

                logger.info(f"Model downloaded to {local_path}")

            except urllib.error.URLError as e:
                raise RuntimeError(f"Failed to download model: {e}")
            except Exception as e:
                # Clean up partial download
                if os.path.exists(local_path):
                    os.remove(local_path)
                raise RuntimeError(f"Model download failed: {e}")
        else:
            logger.info(f"Using cached model at {local_path}")

        # Validate downloaded file
        if not os.path.exists(local_path):
            raise RuntimeError(f"Model download failed: file not created")

        if os.path.getsize(local_path) == 0:
            os.remove(local_path)
            raise RuntimeError("Downloaded model file is empty")

        return local_path
    else:
        # Validate local path
        try:
            validated_path = validate_file_path(
                model_path,
                must_exist=True,
                allowed_extensions=['.pt', '.pth', '.onnx', '.tflite', '.h5', '.pb']
            )
            return validated_path
        except ValidationError as e:
            raise ValidationError(f"Invalid model path: {e}")
        except Exception as e:
            raise FileNotFoundError(f"Model file not found or invalid: {model_path} ({e})")


async def predict_with_tiles(
    model_path: str,
    zoom_level: int,
    tms_url: str = "https://apps.kontur.io/raster-tiler/oam/mosaic/{z}/{x}/{y}.png",
    base_path: Optional[str] = None,
    confidence: float = 0.5,
    area_threshold: float = 3.0,
    tolerance: float = 0.5,
    remove_metadata: bool = True,
    orthogonalize: bool = True,
    vectorization_algorithm: str = "rasterio",
    bbox: Optional[List[float]] = None,
    geojson: Optional[Union[str, dict]] = None,
    crs: str = "3857",
    max_tiles: int = 1000,
    timeout: int = 3600,
) -> Dict:
    """
    End-to-end prediction pipeline with comprehensive validation and error handling.

    Args:
        model_path: Path to model file or URL
        zoom_level: Zoom level for tile downloading (0-22)
        tms_url: TMS URL template for downloading tiles
        base_path: Base directory for processing (optional)
        confidence: Confidence threshold for predictions (0.0-1.0)
        area_threshold: Minimum area threshold for polygons (sq meters, ≥0)
        tolerance: Tolerance for polygon simplification (meters, ≥0)
        remove_metadata: Whether to clean up intermediate files
        orthogonalize: Whether to orthogonalize geometries
        vectorization_algorithm: Algorithm for vectorization ('potrace' or 'rasterio')
        bbox: Bounding box [xmin, ymin, xmax, ymax] in WGS84
        geojson: GeoJSON for area of interest
        crs: Coordinate reference system ('4326' or '3857')
        max_tiles: Maximum number of tiles to process (safety limit)
        timeout: Maximum processing time in seconds

    Returns:
        GeoJSON dictionary with predictions

    Raises:
        ValidationError: If input parameters are invalid
        SecurityError: If inputs pose security risks
        RuntimeError: If processing fails
        TimeoutError: If processing exceeds timeout
    """
    start_time = time.time()

    # Comprehensive input validation
    logger.info("Starting prediction pipeline with validation...")

    try:
        # Validate required inputs
        if not bbox and not geojson:
            raise ValidationError("Either bbox or geojson must be provided")

        # Validate individual parameters
        zoom_level = validate_zoom_level(zoom_level)
        confidence = validate_confidence(confidence)
        area_threshold = validate_area_threshold(area_threshold)
        crs = validate_crs(crs)

        if tolerance < 0:
            raise ValidationError(f"Tolerance must be non-negative, got {tolerance}")

        if vectorization_algorithm not in ["potrace", "rasterio"]:
            raise ValidationError(f"Unsupported vectorization algorithm: {vectorization_algorithm}")

        if not isinstance(max_tiles, int) or max_tiles <= 0:
            raise ValidationError(f"max_tiles must be a positive integer, got {max_tiles}")

        if not isinstance(timeout, int) or timeout <= 0:
            raise ValidationError(f"timeout must be a positive integer, got {timeout}")

        # Validate bbox if provided
        if bbox:
            bbox = validate_bbox(bbox)
            logger.info(f"Validated bbox: {bbox}")

        # Validate geojson if provided
        if geojson:
            from ..validation import validate_geojson
            geojson = validate_geojson(geojson)
            logger.info("Validated GeoJSON input")

        # Validate TMS URL
        tms_url = validate_url(tms_url)
        logger.info(f"Validated TMS URL: {tms_url}")

    except (ValidationError, SecurityError) as e:
        logger.error(f"Input validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        raise ValidationError(f"Input validation failed: {e}")

    # Estimate tile count for safety check
    try:
        from ..utils import get_tiles
        estimated_tiles = get_tiles(zoom=zoom_level, geojson=geojson, bbox=bbox)
        if len(estimated_tiles) > max_tiles:
            raise ValidationError(
                f"Too many tiles required: {len(estimated_tiles)} > {max_tiles}. "
                f"Reduce area or zoom level, or increase max_tiles parameter."
            )
        logger.info(f"Estimated tiles to process: {len(estimated_tiles)}")
    except Exception as e:
        logger.warning(f"Could not estimate tile count: {e}")

    # Download/validate model with error handling
    try:
        model_path = download_or_validate_model(model_path)
        logger.info(f"Model validated/downloaded: {model_path}")
    except Exception as e:
        logger.error(f"Model validation/download failed: {e}")
        raise RuntimeError(f"Model preparation failed: {e}")

    # Setup working directory
    if base_path:
        base_path = os.path.join(base_path, "prediction", str(uuid.uuid4()))
    else:
        base_path = os.path.join(os.getcwd(), "prediction", str(uuid.uuid4()))

    # Download/validate model
    model_path = download_or_validate_model(model_path)

    try:
        os.makedirs(base_path, exist_ok=True)

        # Step 1: Download tiles
        print("Step 1: Downloading tiles...")
        download_path = os.path.join(base_path, "image")
        os.makedirs(download_path, exist_ok=True)

        image_download_path = await download_tiles(
            bbox=bbox,
            geojson=geojson,
            zoom=zoom_level,
            tms=tms_url,
            out=download_path,
            georeference=True,
            crs=crs,
        )

        # Step 2: Run prediction
        print("Step 2: Running model inference...")
        prediction_path = os.path.join(base_path, "prediction")
        os.makedirs(prediction_path, exist_ok=True)

        basic_predict(
            checkpoint_path=model_path,
            input_path=image_download_path,
            prediction_path=prediction_path,
            confidence=confidence,
            remove_images=False,  # Keep for merging
        )

        # Step 3: Merge prediction masks
        print("Step 3: Merging prediction masks...")
        prediction_merged_mask_path = os.path.join(base_path, "merged_prediction_mask.tif")
        merge_rasters(prediction_path, prediction_merged_mask_path)

        # Step 4: Vectorize predictions
        print("Step 4: Vectorizing predictions...")
        start = time.time()

        geojson_path = os.path.join(base_path, "geojson")
        os.makedirs(geojson_path, exist_ok=True)
        prediction_geojson_path = os.path.join(geojson_path, "prediction.geojson")

        converter = VectorizeMasks(
            simplify_tolerance=tolerance,
            min_area=area_threshold,
            orthogonalize=orthogonalize,
            algorithm=vectorization_algorithm,
            tmp_dir=os.path.join(base_path, "tmp"),
        )
        gdf = converter.convert(prediction_merged_mask_path, prediction_geojson_path)

        print(f"Vectorization took {round(time.time() - start)} seconds")

        # Step 5: Reproject to WGS84 if needed
        if gdf.crs and gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        elif not gdf.crs:
            # If not defined, assume it's the same as input CRS
            gdf.set_crs(f"EPSG:{crs}", inplace=True)
            gdf = gdf.to_crs("EPSG:4326")

        # Add metadata
        gdf["building"] = "yes"
        gdf["source"] = "fAIr"

        # Convert to GeoJSON
        prediction_geojson_data = json.loads(gdf.to_json())

        return prediction_geojson_data

    finally:
        # Cleanup if requested
        if remove_metadata and os.path.exists(base_path):
            shutil.rmtree(base_path)
            print("Cleaned up intermediate files")


def run_prediction(
    model_path: str,
    input_path: str,
    prediction_path: str,
    confidence: float = 0.5,
    crs: str = "3857",
) -> str:
    """
    Run prediction on a directory of images.

    Args:
        model_path: Path to model file
        input_path: Directory containing input images
        prediction_path: Directory for prediction outputs
        confidence: Confidence threshold
        crs: Coordinate reference system

    Returns:
        Path to prediction directory
    """
    # Validate model path
    model_path = download_or_validate_model(model_path)

    # Run basic prediction
    basic_predict(
        checkpoint_path=model_path,
        input_path=input_path,
        prediction_path=prediction_path,
        confidence=confidence,
        remove_images=False,
    )

    return prediction_path


# Default model URLs for easy access
DEFAULT_OAM_TMS_MOSAIC = "https://apps.kontur.io/raster-tiler/oam/mosaic/{z}/{x}/{y}.png"
DEFAULT_YOLO_MODEL_V1 = "https://api-prod.fair.hotosm.org/api/v1/workspace/download/yolo/yolov8s_v1-seg.onnx"
DEFAULT_RAMP_MODEL = "https://api-prod.fair.hotosm.org/api/v1/workspace/download/ramp/baseline.tflite"
DEFAULT_YOLO_MODEL_V2 = "https://api-prod.fair.hotosm.org/api/v1/workspace/download/yolo/yolov8s_v2-seg.onnx"
