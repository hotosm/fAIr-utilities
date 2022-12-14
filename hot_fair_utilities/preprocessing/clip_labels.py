# Standard library imports
import os
from glob import glob
from pathlib import Path

# Third-party imports
import geopandas
from osgeo import gdal
from shapely.geometry import box
from tqdm import tqdm

from ..utils import get_bounding_box


def clip_labels(
    input_path: str, output_path: str, rasterize=False, rasterize_options=None
) -> None:
    """Clip and rasterize the GeoJSON labels for each aerial image.

    For each of the OAM images, the corresponding GeoJSON files are
    clipped first and saved in the "labels" directory.
    Then, the clipped GeoJSON files are converted to GeoTIFF files
    and saved in the "binarymasks" or "grayscale_labels"
    directories if the corresponding rasterizing options are chosen.

    The EPSG:3857 projected coordinate system is used
    ('WGS 84 / Pseudo-Mercator', coordinates in meters).

    Args:
        input_path: Path of the directory with input data.
        output_path: Path of the directory where the directories with
            output data will be created.
        rasterize: Whether to rasterize the clipped labels.
        rasterize_options: A list with options how to rasterize the
            label, if rasterize=True. Possible options: "grayscale"
            (burn value will be 255, white buildings on black
            background), "binary" (burn value will be 1, can be used
            for the ramp model).
            If rasterize=False, rasterize_options will be ignored.
    """
    # Check if rasterizing options are valid and create the directories
    # for the output
    if rasterize:
        assert (
            rasterize_options is not None
            and isinstance(rasterize_options, list)
            and 0 < len(rasterize_options) <= 2
            and len(rasterize_options) == len(set(rasterize_options))
        ), "Please provide a list with rasterizing options"

        for option in rasterize_options:
            assert option in (
                "grayscale",
                "binary",
            ), "Please provide a list with valid rasterizing options"

            if option == "grayscale":
                output_grayscale_path = f"{output_path}/grayscale_labels"
                os.makedirs(output_grayscale_path, exist_ok=True)

            if option == "binary":
                output_binary_path = f"{output_path}/binarymasks"
                os.makedirs(output_binary_path, exist_ok=True)

    # Create a directory where the clipped GeoJSON labels will be placed
    output_geojson_path = f"{output_path}/labels"
    os.makedirs(output_geojson_path, exist_ok=True)

    # Clipping GeoJSON labels
    for path in tqdm(
        glob(f"{input_path}/*.png"), desc=f"Clipping labels for {Path(input_path).stem}"
    ):
        filename = Path(path).stem
        geojson_file_all_labels = f"{output_path}/labels_epsg3857.geojson"
        clipped_geojson_file = f"{output_geojson_path}/{filename}.geojson"

        # Bounding box as a tuple
        x_min, y_min, x_max, y_max = get_bounding_box(filename)
        # Bounding box as a polygon
        bounding_box_polygon = box(x_min, y_min, x_max, y_max)

        # Read all labels into a GeoDataFrame, clip it and
        # write to GeoJSON
        gdf_all_labels = geopandas.read_file(geojson_file_all_labels)
        gdf_clipped = gdf_all_labels.clip(bounding_box_polygon)
        if len(gdf_clipped) > 0:
            gdf_clipped.to_file(clipped_geojson_file)
        else:
            schema = {"geometry": "Polygon", "properties": {"id": "int"}}
            crs = "EPSG:3857"
            gdf_clipped.to_file(clipped_geojson_file, schema=schema, crs=crs)

        # Rasterizing
        if rasterize:
            for option in rasterize_options:
                if option == "grayscale":
                    raster_file = f"{output_grayscale_path}/{filename}.tif"
                    burn_values = [255]

                if option == "binary":
                    raster_file = f"{output_binary_path}/{filename}.mask.tif"
                    burn_values = [1]

                # Rasterize clipped labels
                _ = gdal.Rasterize(
                    destNameOrDestDS=raster_file,
                    srcDS=clipped_geojson_file,
                    format="GTiff",
                    outputType=gdal.GDT_Byte,
                    outputBounds=[x_min, y_min, x_max, y_max],
                    width=256,
                    height=256,
                    burnValues=burn_values,
                )
                # Close raster dataset
                _ = None
