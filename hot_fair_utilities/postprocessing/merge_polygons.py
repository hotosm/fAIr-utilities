# Standard library imports
from concurrent.futures import ThreadPoolExecutor

# Third party imports
from geopandas import GeoSeries, read_file
from shapely.geometry import MultiPolygon, Polygon
from shapely.validation import make_valid

from .utils import UndirectedGraph, make_index, project, union

TOLERANCE = 1e-6
SOURCE_CRS = "EPSG:4326"
INTERMEDIATE_CRS = "EPSG:3395"


def buffered(shape, distance_threshold):
    projected = project(shape, SOURCE_CRS, INTERMEDIATE_CRS)
    buffered = projected.buffer(distance_threshold)
    unprojected = project(buffered, INTERMEDIATE_CRS, SOURCE_CRS)

    return unprojected


def unbuffered(shape, distance_threshold):
    projected = project(shape, SOURCE_CRS, INTERMEDIATE_CRS)
    unbuffered = projected.buffer(-1 * distance_threshold)
    unprojected = project(unbuffered, INTERMEDIATE_CRS, SOURCE_CRS)

    return unprojected


def build_graph(idx, shapes, embiggened, i, graph, distance_threshold):
    nearest = [j for j in idx.intersection(embiggened.bounds, objects=False) if i != j]

    for t in nearest:
        if embiggened.intersects(shapes[t]):
            graph.add_edge(i, t)


def merge_components(component, shapes, buffered, unbuffered, distance_threshold):
    embiggened = [buffered(shapes[v], distance_threshold) for v in component]
    merged = unbuffered(union(embiggened), distance_threshold)

    feature = make_valid(merged)

    if type(feature) == MultiPolygon:
        return [
            polygon
            for polygon in feature.geoms
            if type(polygon) == Polygon and polygon.area > 0
        ]
    elif type(feature) == Polygon:
        return [feature]
    return []


def merge_polygons(polygons_path, new_polygons_path, distance_threshold):
    gdf = read_file(polygons_path)
    shapes = list(gdf["geometry"])

    graph = UndirectedGraph()
    idx = make_index(shapes)

    with ThreadPoolExecutor() as executor:
        for i, shape in enumerate(shapes):
            embiggened = buffered(shape, distance_threshold)
            graph.add_edge(i, i)
            executor.submit(
                build_graph, idx, shapes, embiggened, i, graph, distance_threshold
            )

    components = list(graph.components())
    assert sum([len(v) for v in components]) == len(
        shapes
    ), "components capture all shape indices"

    features = []

    with ThreadPoolExecutor() as executor:
        for component in components:
            features.extend(
                merge_components(
                    component, shapes, buffered, unbuffered, distance_threshold
                )
            )

    gs = GeoSeries(features).set_crs(SOURCE_CRS)
    gs.simplify(TOLERANCE).to_file(new_polygons_path)
