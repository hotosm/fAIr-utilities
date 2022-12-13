# Third-party imports
import geopandas


def reproject_labels_to_epsg3857(input_path: str, output_path: str) -> None:
    """Convert a GeoJSON file with labels from EPSG:4326 to EPSG:3857.

    A new GeoJSON file is created, it contains coordinates in meters
    (easting, northing) in the 'WGS 84 / Pseudo-Mercator' projection.

    Args:
        input_path: Path to the GeoJSON file where the input data are stored.
        output_path: Path to the GeoJSON file where the output data will go.
    """
    labels_gdf = geopandas.read_file(input_path).set_crs("EPSG:4326")
    labels_gdf.to_crs("EPSG:3857").to_file(output_path)
