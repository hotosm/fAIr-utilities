# Standard library imports
import os
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from pathlib import Path

# Third party imports
from osgeo import gdal
from tqdm import tqdm

from .utils import get_bounding_box


def georeference_image(path, input_path, output_path, is_mask):
    filename = Path(path).stem
    in_file = f"{input_path}/{filename}.png"
    out_file = f"{output_path}/{filename}.tif"

    x_min, y_min, x_max, y_max = get_bounding_box(filename)

    bands = [1] if is_mask else [1, 2, 3]

    _ = gdal.Translate(
        destName=out_file,
        srcDS=in_file,
        format="GTiff",
        bandList=bands,
        outputBounds=[x_min, y_max, x_max, y_min],
        outputSRS="EPSG:3857",
    )
    _ = None


def georeference(input_path: str, output_path: str, is_mask=False) -> None:
    """Perform georeferencing and remove the fourth band from images (if any).

    CRS of the georeferenced images will be EPSG:3857 ('WGS 84 / Pseudo-Mercator').

    Args:
        input_path: Path of the directory where the input data are stored.
        output_path: Path of the directory where the output data will go.
        is_mask: Whether the image is binary or not.

    Example::

        georeference(
            "data/prediction-dataset/5x5/1-19",
            "data/georeferenced_input/1-19"
        )
    """
    os.makedirs(output_path, exist_ok=True)

    image_paths = glob(f"{input_path}/*.png")

    with ThreadPoolExecutor() as executor:
        for path in image_paths:
            executor.submit(georeference_image, path, input_path, output_path, is_mask)
