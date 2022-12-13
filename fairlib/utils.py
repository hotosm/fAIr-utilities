import math
import os
import re
from glob import glob
from typing import Tuple

# Third-party imports
import geopandas
from shapely.geometry import box

IMAGE_SIZE = 256


def get_prefix(path: str) -> str:
    """Get filename prefix (without extension) from full path."""
    filename = os.path.basename(path)
    return os.path.splitext(filename)[0]


def get_bounding_box(filename: str) -> Tuple[float, float, float, float]:
    """Get the EPSG:3857 coordinates of bounding box for the OAM image.

    This function gives the coordinates of lower left and upper right
    corners of the OAM image. We will use the bounding box to georeference
    the image and for clipping and rasterizing the corresponding labels.

    Returns:
        A tuple, (x_min, y_min, x_max, y_max), with coordinates in meters.
    """
    _, *tile_info = re.split("-", filename)
    x_tile, y_tile, zoom = map(int, tile_info)

    # Lower left and upper right corners in degrees
    x_min, y_min = num2deg(x_tile, y_tile + 1, zoom)
    x_max, y_max = num2deg(x_tile + 1, y_tile, zoom)

    # Create a GeoDataFrame containing a polygon for bounding box
    box_4326 = box(x_min, y_min, x_max, y_max)
    gdf_4326 = geopandas.GeoDataFrame({"geometry": [box_4326]}, crs="EPSG:4326")

    # Reproject to EPSG:3857
    gdf_3857 = gdf_4326.to_crs("EPSG:3857")

    # Bounding box in EPSG:3857 as a tuple (x_min, y_min, x_max, y_max)
    box_3857 = gdf_3857.iloc[0, 0].bounds

    return box_3857


def num2deg(x_tile: int, y_tile: int, zoom: int) -> Tuple[float, float]:
    """Convert tile numbers to EPSG:4326 coordinates.

    Convert tile numbers to the WGS84 longitude/latitude coordinates
    (in degrees) of the upper left corner of the tile.

    Args:
        x_tile: Tile X coordinate
        y_tile: Tile Y coordinate
        zoom: Level of detail

    Returns:
        A tuple (longitude, latitude) in degrees.
    """
    n = 2.0**zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)

    return lon_deg, lat_deg


def remove_files(pattern: str) -> None:
    """Remove files matching a wildcard."""
    files = glob(pattern)
    for file in files:
        os.remove(file)
