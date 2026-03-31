import os
import re
from glob import glob
from pathlib import Path

import geopandas
import mercantile
import numpy as np
import rasterio
from rasterio.features import rasterize as rasterize_shapes
from rasterio.transform import from_bounds
from shapely.geometry import box

from .._logging import track


def _bounding_box_from_filename(filename: str, epsg: int = 3857) -> tuple[float, float, float, float]:
    """Extract tile coordinates from an OAM filename and return the bounding box."""
    clean = re.sub(r"\.(png|jpeg)$", "", filename)
    _, *tile_info = re.split("-", clean)
    x_tile, y_tile, zoom = map(int, tile_info)
    tile = mercantile.Tile(x=x_tile, y=y_tile, z=zoom)

    if epsg == 3857:
        bounds = mercantile.xy_bounds(tile)
        return bounds.left, bounds.bottom, bounds.right, bounds.top

    bounds = mercantile.bounds(tile)
    return bounds.west, bounds.south, bounds.east, bounds.north


def clip_labels(
    input_path: str,
    output_path: str,
    rasterize: bool = False,
    rasterize_options: list[str] | None = None,
    all_geojson_file: str | None = None,
    epsg: int = 3857,
) -> None:
    """Clip and rasterize the GeoJSON labels for each aerial image.

    For each OAM image, the corresponding GeoJSON labels are clipped and
    saved in the "labels" directory. Optionally rasterized to GeoTIFF.

    Args:
        input_path: Directory with input PNG images.
        output_path: Directory for output data.
        rasterize: Whether to rasterize clipped labels.
        rasterize_options: List of rasterize modes ("grayscale", "binary").
        all_geojson_file: Path to the GeoJSON file with all labels.
        epsg: EPSG code for the coordinate system.
    """
    output_grayscale_path = ""
    output_binary_path = ""

    if rasterize:
        assert (
            rasterize_options is not None
            and isinstance(rasterize_options, list)
            and 0 < len(rasterize_options) <= 2
            and len(rasterize_options) == len(set(rasterize_options))
        ), "Please provide a list with rasterizing options"

        for option in rasterize_options:
            assert option in ("grayscale", "binary"), "Please provide valid rasterizing options"

            if option == "grayscale":
                output_grayscale_path = f"{output_path}/grayscale_labels"
                os.makedirs(output_grayscale_path, exist_ok=True)

            if option == "binary":
                output_binary_path = f"{output_path}/binarymasks"
                os.makedirs(output_binary_path, exist_ok=True)

    output_geojson_path = f"{output_path}/labels"
    os.makedirs(output_geojson_path, exist_ok=True)

    png_files = glob(f"{input_path}/*.png")
    for path in track(png_files, description=f"Clipping labels for {Path(input_path).stem}"):
        filename = Path(path).stem
        geojson_file_all_labels = all_geojson_file or f"{output_path}/labels_epsg3857.geojson"
        clipped_geojson_file = f"{output_geojson_path}/{filename}.geojson"

        x_min, y_min, x_max, y_max = _bounding_box_from_filename(filename, epsg=epsg)
        bounding_box_polygon = box(x_min, y_min, x_max, y_max)

        gdf_all_labels = geopandas.read_file(os.path.relpath(geojson_file_all_labels))
        gdf_clipped = gdf_all_labels.clip(bounding_box_polygon)
        if len(gdf_clipped) > 0:
            gdf_clipped.to_file(clipped_geojson_file, driver="GeoJSON")
        else:
            with open(clipped_geojson_file, "w", encoding="utf-8") as output_file:
                output_file.write('{"type":"FeatureCollection","name":"labels","features":[]}')

        if rasterize and rasterize_options:
            for option in rasterize_options:
                if option == "grayscale":
                    raster_file = f"{output_grayscale_path}/{filename}.tif"
                    burn_value = 255
                else:
                    raster_file = f"{output_binary_path}/{filename}.mask.tif"
                    burn_value = 1

                mask = np.zeros((256, 256), dtype=np.uint8)
                if not gdf_clipped.empty:
                    mask = rasterize_shapes(
                        ((geometry, burn_value) for geometry in gdf_clipped.geometry),
                        out_shape=mask.shape,
                        fill=0,
                        transform=from_bounds(x_min, y_min, x_max, y_max, mask.shape[1], mask.shape[0]),
                        dtype=mask.dtype,
                    )

                with rasterio.open(
                    raster_file,
                    "w",
                    driver="GTiff",
                    width=mask.shape[1],
                    height=mask.shape[0],
                    count=1,
                    dtype=mask.dtype,
                    crs=f"EPSG:{epsg}",
                    transform=from_bounds(x_min, y_min, x_max, y_max, mask.shape[1], mask.shape[0]),
                ) as dataset:
                    dataset.write(mask, 1)
