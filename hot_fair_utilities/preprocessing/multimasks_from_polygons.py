# Multichannel mask generation from building-polygon GeoJSON files.


from pathlib import Path
import os

import geopandas as gpd
import rasterio as rio
from ._multimask_vendored import (
    open_rasterio,
    build_mask_path,
    is_metric_crs,
    dataframe_to_pixel_mask,
    extract_crs,
    pair_chips_and_labels,
    onehot_to_sparse_mask,
    channels_last_to_first,
)
from tqdm import tqdm


def get_rasterio_shape_and_transform(image_path):
    """Read raster dimensions and affine from a chip file."""
    with rio.open(image_path) as rio_dset:
        shape = rio_dset.shape
        transform = rio_dset.transform
    return shape, transform


def multimasks_from_polygons(
    in_poly_dir,
    in_chip_dir,
    out_mask_dir,
    input_contact_spacing=8,
    input_boundary_width=3,
):
    """Create multichannel building footprint masks from geojson label files.

    Requires a matching image-chips directory.  Units of
    *input_contact_spacing* and *input_boundary_width* are **pixels**:

        Real-world width (m) = pixel width × resolution (m/px)

    Args:
        in_poly_dir: Directory of ``<name>.geojson`` label files.
        in_chip_dir: Directory of ``<name>.tif``     chip  files.
        out_mask_dir: Output directory for ``.mask.tif`` files.
        input_contact_spacing: Contact-zone expansion distance (px).
        input_boundary_width:  Boundary inner-buffer distance (px).

    Example::

        multimasks_from_polygons(
            "data/preprocessed/labels",
            "data/preprocessed/chips",
            "data/preprocessed/multimasks",
        )
    """
    Path(out_mask_dir).mkdir(parents=True, exist_ok=True)

    chip_label_pairs = pair_chips_and_labels(in_chip_dir, in_poly_dir)
    chip_paths, label_paths = list(zip(*chip_label_pairs))

    mask_paths = [
        build_mask_path(out_mask_dir, chip_path) for chip_path in chip_paths
    ]

    for json_path, chip_path, mask_path in tqdm(
        zip(label_paths, chip_paths, mask_paths), desc="Multimasks for input"
    ):
        if Path(mask_path).is_file():
            continue

        mask_shape, mask_transform = get_rasterio_shape_and_transform(chip_path)

        gdf = gpd.read_file(os.path.relpath(json_path))
        gdf = gdf[~gdf["geometry"].isna()]
        gdf = gdf[~gdf.is_empty]

        reference_im = open_rasterio(chip_path)

        if extract_crs(gdf) != extract_crs(reference_im):
            gdf = gdf.to_crs(extract_crs(reference_im))

        if is_metric_crs(gdf):
            meters = True
            boundary_width = min(reference_im.res) * input_boundary_width
            contact_spacing = min(reference_im.res) * input_contact_spacing
        else:
            meters = False
            boundary_width = input_boundary_width
            contact_spacing = input_contact_spacing

        gdf_poly = gdf.explode(ignore_index=True)

        onehot_multi_mask = dataframe_to_pixel_mask(
            df=gdf_poly,
            out_file=mask_path,
            shape=mask_shape,
            do_transform=True,
            affine_obj=None,
            channels=["footprint", "boundary", "contact"],
            reference_im=reference_im,
            boundary_width=boundary_width,
            contact_spacing=contact_spacing,
            out_type="uint8",
            meters=meters,
        )

        sparse_multi_mask = onehot_to_sparse_mask(onehot_multi_mask)
        sparse_multi_mask = channels_last_to_first(sparse_multi_mask)

        with rio.open(chip_path, "r") as src:
            meta = src.meta.copy()
            meta.update(count=sparse_multi_mask.shape[0])
            meta.update(dtype="uint8")
            meta.update(nodata=None)
            with rio.open(mask_path, "w", **meta) as dst:
                dst.write(sparse_multi_mask)
