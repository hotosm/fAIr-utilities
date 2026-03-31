import os
import tempfile
from pathlib import Path

from geomltoolkits import merge_polygons, merge_rasters, vectorize_mask

from .._logging import get_logger

log = get_logger(__name__)


def polygonize(
    input_path: str,
    output_path: str,
    remove_inputs: bool = False,
    tolerance: float = 0.5,
    area_threshold: float = 5.0,
    distance_threshold: float = 0.6,
) -> None:
    """Polygonize raster mask tiles into a merged GeoJSON.

    Steps:
    1. Merge all mask TIFs into a single raster.
    2. Vectorize the merged raster into simplified polygons.
    3. Merge adjacent polygons within a distance threshold.

    CRS of the resulting GeoJSON file will be EPSG:4326.

    Args:
        input_path: Directory containing mask TIF files.
        output_path: Path for the output GeoJSON file.
        remove_inputs: Delete input TIF files after polygonization.
        tolerance: Simplification tolerance in meters.
        area_threshold: Minimum polygon area in square meters.
        distance_threshold: Buffer distance in meters for merging adjacent polygons.
    """
    if os.path.exists(output_path):
        os.remove(output_path)

    base_path = Path(output_path).parent
    base_path.mkdir(exist_ok=True, parents=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        merged_raster = os.path.join(tmp_dir, "merged.tif")
        vectorized_geojson = os.path.join(tmp_dir, "vectorized.geojson")

        merge_rasters(input_path, merged_raster)
        vectorize_mask(
            input_tiff=merged_raster,
            output_geojson=vectorized_geojson,
            simplify_tolerance=tolerance,
            min_area=area_threshold,
            orthogonalize=False,
        )

        merge_polygons(vectorized_geojson, output_path, distance_threshold=distance_threshold)

    log.info("Polygonized %s -> %s", input_path, output_path)

    if remove_inputs:
        for tif_file in Path(input_path).glob("*.tif"):
            tif_file.unlink()
