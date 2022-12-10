import os
from pathlib import Path

from .get_polygons import get_polygons
from .merge_polygons import merge_polygons


def polygonize(input_path: str, output_path: str) -> None:
    """Polygonize raster tiles from the input path using AutoBFE's algorithm.

    There are two steps:
    1. It polygonizes each of the individual tiles first.
    2. Using GDAL buffering, it merges all the nearby polygons
    so that the split polygons get merged into one.

    Whether the images are georeferenced or not doesn't really matter.
    Even PNG images will do.

    CRS of the resulting GeoJSON file will be EPSG:4326.

    Args:
        input_path: Path of the directory where the image files are stored.
        output_path: Path of the output file.

    Example::

        poygonize("data/masks_v2/4", "labels.geojson")
    """
    base_path = Path(output_path).parents[0]
    base_path.mkdir(exist_ok=True, parents=True)

    get_polygons(input_path, "temp-labels.geojson", kernel_opening=1)
    merge_polygons("temp-labels.geojson", output_path, distance_threshold=0.6)
    os.remove("temp-labels.geojson")
