"""
Data acquisition module for downloading tiles and OSM data.

This module provides functionality to download:
- TMS tiles from various sources with async support
- OSM data via HOT Raw Data API
- Support for multiple tile schemes (XYZ, TMS, QuadKey)
- Georeferencing and CRS transformation capabilities
"""

from .tms_downloader import download_tiles, TileSource
from .osm_downloader import download_osm_data, RawDataAPI

__all__ = [
    "download_tiles",
    "TileSource", 
    "download_osm_data",
    "RawDataAPI"
]
