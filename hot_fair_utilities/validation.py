"""
Input validation and security utilities for fAIr-utilities.

This module provides comprehensive input validation, sanitization,
and security checks for all user inputs and external data.
"""

import os
import re
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import geopandas as gpd
from shapely.geometry import Polygon, box


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


def validate_bbox(bbox: List[float]) -> List[float]:
    """
    Validate and sanitize bounding box coordinates.
    
    Args:
        bbox: Bounding box as [xmin, ymin, xmax, ymax]
        
    Returns:
        Validated and sanitized bbox
        
    Raises:
        ValidationError: If bbox is invalid
    """
    if not isinstance(bbox, (list, tuple)):
        raise ValidationError(f"bbox must be a list or tuple, got {type(bbox)}")
    
    if len(bbox) != 4:
        raise ValidationError(f"bbox must have exactly 4 coordinates, got {len(bbox)}")
    
    try:
        bbox = [float(coord) for coord in bbox]
    except (ValueError, TypeError) as e:
        raise ValidationError(f"bbox coordinates must be numeric: {e}")
    
    xmin, ymin, xmax, ymax = bbox
    
    # Validate coordinate ranges
    if not (-180 <= xmin <= 180) or not (-180 <= xmax <= 180):
        raise ValidationError(f"Longitude values must be between -180 and 180: {xmin}, {xmax}")
    
    if not (-90 <= ymin <= 90) or not (-90 <= ymax <= 90):
        raise ValidationError(f"Latitude values must be between -90 and 90: {ymin}, {ymax}")
    
    # Validate bbox geometry
    if xmin >= xmax:
        raise ValidationError(f"xmin ({xmin}) must be less than xmax ({xmax})")
    
    if ymin >= ymax:
        raise ValidationError(f"ymin ({ymin}) must be less than ymax ({ymax})")
    
    # Check bbox size (prevent extremely large areas)
    area = (xmax - xmin) * (ymax - ymin)
    if area > 100:  # More than 100 square degrees
        raise ValidationError(f"Bounding box too large: {area} square degrees. Maximum allowed: 100")
    
    return bbox


def validate_zoom_level(zoom: int) -> int:
    """
    Validate zoom level.
    
    Args:
        zoom: Zoom level
        
    Returns:
        Validated zoom level
        
    Raises:
        ValidationError: If zoom level is invalid
    """
    if not isinstance(zoom, int):
        try:
            zoom = int(zoom)
        except (ValueError, TypeError):
            raise ValidationError(f"Zoom level must be an integer, got {type(zoom)}")
    
    if not (0 <= zoom <= 22):
        raise ValidationError(f"Zoom level must be between 0 and 22, got {zoom}")
    
    return zoom


def validate_crs(crs: str) -> str:
    """
    Validate coordinate reference system.
    
    Args:
        crs: CRS identifier
        
    Returns:
        Validated CRS
        
    Raises:
        ValidationError: If CRS is invalid
    """
    if not isinstance(crs, str):
        raise ValidationError(f"CRS must be a string, got {type(crs)}")
    
    valid_crs = ["4326", "3857", "EPSG:4326", "EPSG:3857"]
    if crs not in valid_crs:
        raise ValidationError(f"Unsupported CRS: {crs}. Supported: {valid_crs}")
    
    # Normalize CRS format
    if crs in ["4326", "EPSG:4326"]:
        return "4326"
    elif crs in ["3857", "EPSG:3857"]:
        return "3857"
    
    return crs


def validate_file_path(file_path: str, must_exist: bool = True, allowed_extensions: Optional[List[str]] = None) -> str:
    """
    Validate and sanitize file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist
        allowed_extensions: List of allowed file extensions
        
    Returns:
        Validated file path
        
    Raises:
        ValidationError: If path is invalid
        SecurityError: If path poses security risk
    """
    if not isinstance(file_path, (str, Path)):
        raise ValidationError(f"File path must be string or Path, got {type(file_path)}")
    
    file_path = str(file_path)
    
    # Security checks
    if ".." in file_path:
        raise SecurityError("Path traversal detected: '..' not allowed in file paths")
    
    if file_path.startswith("/"):
        raise SecurityError("Absolute paths not allowed for security reasons")
    
    # Validate path characters
    if re.search(r'[<>:"|?*]', file_path):
        raise ValidationError("Invalid characters in file path")
    
    # Check file extension if specified
    if allowed_extensions:
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in [ext.lower() for ext in allowed_extensions]:
            raise ValidationError(f"File extension {file_ext} not allowed. Allowed: {allowed_extensions}")
    
    # Check if file exists if required
    if must_exist and not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    return file_path


def validate_url(url: str) -> str:
    """
    Validate and sanitize URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        ValidationError: If URL is invalid
        SecurityError: If URL poses security risk
    """
    if not isinstance(url, str):
        raise ValidationError(f"URL must be a string, got {type(url)}")
    
    # Parse URL
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}")
    
    # Security checks
    if parsed.scheme not in ["http", "https"]:
        raise SecurityError(f"Only HTTP/HTTPS URLs allowed, got {parsed.scheme}")
    
    if not parsed.netloc:
        raise ValidationError("URL must have a valid domain")
    
    # Check for localhost/private IPs (basic check)
    if "localhost" in parsed.netloc.lower() or "127.0.0.1" in parsed.netloc:
        raise SecurityError("Localhost URLs not allowed for security reasons")
    
    return url


def validate_geojson(geojson: Union[str, dict]) -> dict:
    """
    Validate GeoJSON data.
    
    Args:
        geojson: GeoJSON data as string or dict
        
    Returns:
        Validated GeoJSON dict
        
    Raises:
        ValidationError: If GeoJSON is invalid
    """
    if isinstance(geojson, str):
        try:
            import json
            geojson = json.loads(geojson)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
    
    if not isinstance(geojson, dict):
        raise ValidationError(f"GeoJSON must be a dictionary, got {type(geojson)}")
    
    # Basic GeoJSON structure validation
    if "type" not in geojson:
        raise ValidationError("GeoJSON must have a 'type' field")
    
    valid_types = ["Feature", "FeatureCollection", "Polygon", "Point", "LineString", "MultiPolygon"]
    if geojson["type"] not in valid_types:
        raise ValidationError(f"Invalid GeoJSON type: {geojson['type']}. Valid types: {valid_types}")
    
    # Validate geometry if present
    if "geometry" in geojson:
        _validate_geometry(geojson["geometry"])
    
    # Validate features if FeatureCollection
    if geojson["type"] == "FeatureCollection":
        if "features" not in geojson:
            raise ValidationError("FeatureCollection must have 'features' field")
        
        if not isinstance(geojson["features"], list):
            raise ValidationError("Features must be a list")
        
        if len(geojson["features"]) > 10000:
            raise ValidationError("Too many features (max 10,000 for performance)")
    
    return geojson


def _validate_geometry(geometry: dict) -> None:
    """
    Validate geometry object.
    
    Args:
        geometry: Geometry dictionary
        
    Raises:
        ValidationError: If geometry is invalid
    """
    if not isinstance(geometry, dict):
        raise ValidationError("Geometry must be a dictionary")
    
    if "type" not in geometry:
        raise ValidationError("Geometry must have a 'type' field")
    
    if "coordinates" not in geometry:
        raise ValidationError("Geometry must have 'coordinates' field")
    
    # Basic coordinate validation
    coords = geometry["coordinates"]
    if not isinstance(coords, list):
        raise ValidationError("Coordinates must be a list")


def validate_confidence(confidence: float) -> float:
    """
    Validate confidence threshold.
    
    Args:
        confidence: Confidence value
        
    Returns:
        Validated confidence
        
    Raises:
        ValidationError: If confidence is invalid
    """
    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        raise ValidationError(f"Confidence must be a number, got {type(confidence)}")
    
    if not (0.0 <= confidence <= 1.0):
        raise ValidationError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
    
    return confidence


def validate_area_threshold(area: float) -> float:
    """
    Validate area threshold.
    
    Args:
        area: Area threshold in square meters
        
    Returns:
        Validated area threshold
        
    Raises:
        ValidationError: If area is invalid
    """
    try:
        area = float(area)
    except (ValueError, TypeError):
        raise ValidationError(f"Area threshold must be a number, got {type(area)}")
    
    if area < 0:
        raise ValidationError(f"Area threshold must be non-negative, got {area}")
    
    if area > 1000000:  # 1 square kilometer
        raise ValidationError(f"Area threshold too large: {area} sq meters. Maximum: 1,000,000")
    
    return area


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not isinstance(filename, str):
        raise ValidationError(f"Filename must be a string, got {type(filename)}")
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    filename = re.sub(r'[\x00-\x1f]', '', filename)  # Remove control characters
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    # Ensure not empty
    if not filename.strip():
        filename = "unnamed_file"
    
    return filename
