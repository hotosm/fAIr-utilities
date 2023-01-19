# Standard library imports
import os
from glob import glob
from pathlib import Path

# Third party imports
# Third-party imports
from osgeo import gdal
from tqdm import tqdm

from .utils import get_bounding_box


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

    for path in tqdm(
        glob(f"{input_path}/*.png"), desc=f"Georeferencing for {Path(input_path).stem}"
    ):
        filename = Path(path).stem
        in_file = f"{input_path}/{filename}.png"
        out_file = f"{output_path}/{filename}.tif"

        # Get bounding box in EPSG:3857
        x_min, y_min, x_max, y_max = get_bounding_box(filename)

        # Use one band for masks and the first three bands for images
        bands = [1] if is_mask else [1, 2, 3]

        # Georeference image
        # Output bounds are defined by upper left and lower right corners
        _ = gdal.Translate(
            destName=out_file,
            srcDS=in_file,
            format="GTiff",
            bandList=bands,
            outputBounds=[x_min, y_max, x_max, y_min],
            outputSRS="EPSG:3857",
        )
        # Close dataset
        _ = None
