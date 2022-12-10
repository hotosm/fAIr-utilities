from glob import glob
from pathlib import Path

import numpy as np
import rasterio as rio
from geopandas import GeoSeries
from rasterio.features import shapes
from rasterio.merge import merge
from shapely.geometry import Polygon, shape
from tqdm import tqdm

TOLERANCE = 1
AREA_THRESHOLD = 0.1
MAX_RATIO = 10


def vectorize(input_path: str, output_path: str) -> None:
    """Polygonize raster tiles from the input path.

    Note that as input, we are expecting GeoTIF images with EPSG:3857 as
    CRS here. CRS of the resulting GeoJSON file will be EPSG:4326.

    Args:
        input_path: Path of the directory where the TIF files are stored.
        output_path: Path of the output file.

    Example::

        vectorize("data/masks_v2/4", "labels.geojson")
    """
    base_path = Path(output_path).parents[0]
    base_path.mkdir(exist_ok=True, parents=True)

    rasters = []
    for path in glob(f"{input_path}/*.tif"):
        raster = rio.open(path)
        rasters.append(raster)

    mosaic, output = merge(rasters)
    polygons = [shape(s) for s, _ in shapes(mosaic, transform=output)]

    areas = [poly.area for poly in polygons]
    max_area, median_area = np.max(areas), np.median(areas)
    polygons = [
        Polygon(poly.exterior.coords)
        for poly in polygons
        if poly.area != max_area and poly.area / median_area > AREA_THRESHOLD
    ]

    gs = GeoSeries(polygons).set_crs("EPSG:3857").simplify(TOLERANCE)
    gs = remove_overlapping_polygons(gs)
    gs.to_crs("EPSG:4326").to_file(output_path)


def remove_overlapping_polygons(gs: GeoSeries) -> GeoSeries:
    """Remove overlapping polygons.

    Args:
        gs: List of polygons to be fixed.
    """
    to_remove = set()
    for i in tqdm(range(len(gs))):
        for j in range(i + 1, len(gs)):
            p, q = gs.iloc[i], gs.iloc[j]

            if GeoSeries(p).overlaps(q).bool():
                ratio = max(p.area, q.area) / min(p.area, q.area)
                if ratio > MAX_RATIO:
                    to_remove.add(i if p.area < q.area else j)

    return gs.drop(list(to_remove))
