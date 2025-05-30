"""
Vectorization module for converting raster masks to vector polygons.

This module provides advanced vectorization capabilities including:
- Potrace-based vectorization for smooth curves
- Rasterio-based vectorization for direct conversion
- Geometry regularization and orthogonalization
- Advanced polygon cleaning and simplification
"""

from .regularizer import VectorizeMasks
from .orthogonalize import orthogonalize_gdf

__all__ = [
    "VectorizeMasks",
    "orthogonalize_gdf"
]
