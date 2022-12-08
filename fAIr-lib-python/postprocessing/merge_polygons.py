from geopandas import GeoSeries, read_file
from shapely.geometry import MultiPolygon, Polygon
from shapely.validation import make_valid
from tqdm import tqdm

from .utils import UndirectedGraph, make_index, project, union

TOLERANCE = 1e-6
SOURCE_CRS = "EPSG:4326"
INTERMEDIATE_CRS = "EPSG:3395"


def merge_polygons(polygons_path, new_polygons_path, distance_threshold):
    """Merge polygons from GeoJSON file.

    Args:
      polygons_path: GeoJSON file to read polygons from
      new_polygons_path: Path to GeoJSON file where the merged polygons will be saved
      distance_threshold: Minimum distance to define adjacent polygons, in meters
    """
    gdf = read_file(polygons_path)
    shapes = list(gdf["geometry"])

    graph = UndirectedGraph()
    idx = make_index(shapes)

    def buffered(shape):
        projected = project(shape, SOURCE_CRS, INTERMEDIATE_CRS)
        buffered = projected.buffer(distance_threshold)
        unprojected = project(buffered, INTERMEDIATE_CRS, SOURCE_CRS)

        return unprojected

    def unbuffered(shape):
        projected = project(shape, SOURCE_CRS, INTERMEDIATE_CRS)
        unbuffered = projected.buffer(-1 * distance_threshold)
        unprojected = project(unbuffered, INTERMEDIATE_CRS, SOURCE_CRS)

        return unprojected

    for i, shape in enumerate(tqdm(shapes, desc="Building graph", unit="shapes")):
        embiggened = buffered(shape)
        graph.add_edge(i, i)
        nearest = [
            j for j in idx.intersection(embiggened.bounds, objects=False) if i != j
        ]

        for t in nearest:
            if embiggened.intersects(shapes[t]):
                graph.add_edge(i, t)

    components = list(graph.components())
    assert sum([len(v) for v in components]) == len(
        shapes
    ), "components capture all shape indices"

    features = []

    for component in tqdm(components, desc="Merging components", unit="component"):
        embiggened = [buffered(shapes[v]) for v in component]
        merged = unbuffered(union(embiggened))

        feature = make_valid(merged)

        if type(feature) == MultiPolygon:
            for polygon in feature.geoms:
                if type(polygon) == Polygon and polygon.area > 0:
                    features.append(polygon)
        elif type(feature) == Polygon:
            features.append(feature)

    gs = GeoSeries(features).set_crs(SOURCE_CRS)
    gs.simplify(TOLERANCE).to_file(new_polygons_path)
