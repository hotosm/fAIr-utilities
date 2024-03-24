# Standard library imports
import os

from ..georeferencing import georeference
from .clip_labels import clip_labels
from .fix_labels import fix_labels
from .multimasks_from_polygons import multimasks_from_polygons
from .reproject_labels import reproject_labels_to_epsg3857


def preprocess(
    input_path: str,
    output_path: str,
    rasterize=False,
    rasterize_options=None,
    georeference_images=False,
    multimasks=False,
    input_contact_spacing=4,  # only required if multimasks is set to true
    input_boundary_width=2,  # only required if mulltimasks is set to true
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
            "multimasks" - for the multimasks labels (if multimasks=True)
        rasterize: Whether to create the raster labels.
        rasterize_options: A list with options how to rasterize the
            label, if rasterize=True. Possible options: "grayscale"
            (burn value will be 255, white buildings on black
            background), "binary" (burn value will be 1, can be used
            for the ramp model).
            If rasterize=False, rasterize_options will be ignored.
        georeference_images: Whether to georeference the OAM images.
        multimasks: Whether to additionally output multimask labels.
        input_contact_spacing (int, optional): Width in pixel units of boundary class around building footprints,
            in pixels. This variable is about creating a visible, protective bubble around each building, and you get to decide how thick this bubble is.
        input_boundary_width (int, optional): Pixels that are closer to two different polygons than contact_spacing
            (in pixel units) will be labeled with the contact mask. This variable  is about what happens when two buildings' bubbles are about to touch or overlap; it switches to a different kind of marking to show the boundary clearly between them, ensuring each building's space is respected.

        Unit of input_contact_spacing and input_boundary_width is in pixel width which is :

        Real-world width (in meters)= Pixel width×Resolution (meters per pixel)

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

    if multimasks:
        assert os.path.isdir(
            f"{output_path}/chips"
        ), "Chips do not exist. Set georeference_images=True."
        multimasks_from_polygons(
            f"{output_path}/labels",
            f"{output_path}/chips",
            f"{output_path}/multimasks",
            input_contact_spacing=input_contact_spacing,
            input_boundary_width=input_boundary_width,
        )
