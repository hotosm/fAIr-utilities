import geopandas
from shapely.validation import explain_validity, make_valid


def remove_self_intersection(row):
    """Fix self-intersections in the polygons.

    Some of the polygons may have self-intersections. In that
    case, we transform that geometry to a multi-polygon and
    substitute the original geometry with the largest polygon.
    """
    if explain_validity(row.geometry) == "Valid Geometry":
        return row.geometry

    valid_geom = make_valid(row.geometry)
    if not hasattr(valid_geom, "__len__"):
        return valid_geom

    for polygon in valid_geom.geoms:
        if polygon.area >= row.geometry.area / 2.0:
            return polygon


def fix_labels(input_path: str, output_path: str) -> None:
    """Fix GeoJSON file so that it doesn't have any self-intersecting polygons.

    Args:
        input_path: Path to the GeoJSON file where the input data are stored.
        output_path: Path to the GeoJSON file where the output data will go.
    """
    gdf = geopandas.read_file(input_path)
    gdf["geometry"] = gdf.apply(remove_self_intersection, axis=1)
    gdf.to_file(output_path)
