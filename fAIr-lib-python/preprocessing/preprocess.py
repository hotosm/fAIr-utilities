# Standard library imports
import os

from ..georeferencing import georeference
from .clip_labels import clip_labels
from .fix_labels import fix_labels
from .reproject_labels import reproject_labels_to_epsg3857


def preprocess(
    input_path: str,
    output_path: str,
    rasterize=False,
    rasterize_options=None,
    georeference_images=False,
) -> None:
    """Fully preprocess the input data.

    The preprocessed images and labels are in the EPSG:3857 projected
    coordinate system ('WGS 84 / Pseudo-Mercator', coordinates
    in meters).

    Args:
        input_path: Path of the directory with input data.
        output_path: Path of the directory where to put the preprocessed
            data. New directories will be created in this directory:
            "labels" - for the clipped GeoJSON labels,
            "chips" - for the georeferenced OAM images
            (if georeference_images=True), and the directories
            "binarymasks" and "grayscale_labels" if the corresponding
            rasterizing options are chosen.
        rasterize: Whether to create the raster labels.
        rasterize_options: A list with options how to rasterize the
            label, if rasterize=True. Possible options: "grayscale"
            (burn value will be 255, white buildings on black
            background), "binary" (burn value will be 1, can be used
            for the ramp model).
            If rasterize=False, rasterize_options will be ignored.
        georeference_images: Whether to georeference the OAM images.

    Example::

        preprocess(
            "data/region1_inputs",
            "data/region1_preprocessed",
            rasterize=True,
            rasterize_options=["grayscale", "binary"],
            georeference_images=True
        )
    """
    # Check if rasterizing options are valid
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

    os.makedirs(output_path, exist_ok=True)

    if georeference_images:
        georeference(input_path, f"{output_path}/chips")

    fix_labels(
        f"{input_path}/labels.geojson",
        f"{output_path}/corrected_labels.geojson",
    )

    reproject_labels_to_epsg3857(
        f"{output_path}/corrected_labels.geojson",
        f"{output_path}/labels_epsg3857.geojson",
    )

    clip_labels(input_path, output_path, rasterize, rasterize_options)

    os.remove(f"{output_path}/corrected_labels.geojson")
    os.remove(f"{output_path}/labels_epsg3857.geojson")
