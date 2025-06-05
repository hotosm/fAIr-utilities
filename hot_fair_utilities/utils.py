# Standard library imports
import concurrent.futures
import io
import gc
import json
import math
import os
import re
import time
import urllib.request
import zipfile
from glob import glob
from typing import Tuple

# Third party imports
# Third-party imports
import geopandas
import matplotlib.pyplot as plt
import mercantile
import pandas as pd
import rasterio
from rasterio.merge import merge
import requests
import ultralytics
from shapely.geometry import box
import shapely.geometry

IMAGE_SIZE = 256


def get_prefix(path: str) -> str:
    """Get filename prefix (without extension) from full path."""
    filename = os.path.basename(path)
    return os.path.splitext(filename)[0]


def get_bounding_box(filename: str, epsg=3857) -> Tuple[float, float, float, float]:
    """Get the EPSG:3857 coordinates of bounding box for the OAM image.

    This function gives the coordinates of lower left and upper right
    corners of the OAM image. We will use the bounding box to georeference
    the image and for clipping and rasterizing the corresponding labels.

    Returns:
        A tuple, (x_min, y_min, x_max, y_max), with coordinates in meters.
    """
    filename = re.sub(r"\.(png|jpeg)$", "", filename)
    _, *tile_info = re.split("-", filename)
    x_tile, y_tile, zoom = map(int, tile_info)

    # Lower left and upper right corners in degrees
    x_min, y_min = num2deg(x_tile, y_tile + 1, zoom)
    x_max, y_max = num2deg(x_tile + 1, y_tile, zoom)

    # Create a GeoDataFrame containing a polygon for bounding box
    box_4326 = box(x_min, y_min, x_max, y_max)
    gdf_4326 = geopandas.GeoDataFrame({"geometry": [box_4326]}, crs="EPSG:4326")

    # Reproject to EPSG:3857

    gdf_3857 = gdf_4326.to_crs(f"EPSG:{epsg}")

    # Bounding box in EPSG:3857 as a tuple (x_min, y_min, x_max, y_max)
    box_3857 = gdf_3857.iloc[0, 0].bounds

    return box_3857


def num2deg(x_tile: int, y_tile: int, zoom: int) -> Tuple[float, float]:
    """Convert tile numbers to EPSG:4326 coordinates.

    Convert tile numbers to the WGS84 longitude/latitude coordinates
    (in degrees) of the upper left corner of the tile.

    Args:
        x_tile: Tile X coordinate
        y_tile: Tile Y coordinate
        zoom: Level of detail

    Returns:
        A tuple (longitude, latitude) in degrees.
    """
    n = 2.0**zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)

    return lon_deg, lat_deg


def remove_files(pattern: str) -> None:
    """Remove files matching a wildcard."""
    files = glob(pattern)
    for file in files:
        os.remove(file)


def convert2worldcd(lat, lng, tile_size):
    """
    World coordinates  are measured from the Mercator projection's origin
    (the northwest corner of the map at 180 degrees longitude and
    approximately 85 degrees latitude) and increase in the x direction
    towards the east (right) and increase in the y direction towards the south
    (down).Because the basic Mercator  tile is 256 x 256 pixels, the usable
    world coordinate space is {0-256}, {0-256}
    """
    siny = math.sin((lat * math.pi) / 180)
    siny = min(max(siny, -0.9999), 0.9999)
    world_x = tile_size * (0.5 + (lng / 360))
    world_y = tile_size * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))
    # print("world coordinate space is %s, %s",world_x,world_y)
    return world_x, world_y


def latlng2tile(zoom, lat, lng, tile_size):
    """By dividing the pixel coordinates by the tile size and taking the
    integer parts of the result, you produce as a by-product the tile
    coordinate at the current zoom level."""
    zoom_byte = 1 << zoom  # converting zoom level to pixel bytes
    # print(zoom_byte)
    w_x, w_y = convert2worldcd(lat, lng, tile_size)

    t_x = math.floor((w_x * zoom_byte) / tile_size)
    t_y = math.floor((w_y * zoom_byte) / tile_size)
    return t_x, t_y


def bbox2tiles(bbox_coords, zm_level, tile_size):
    # start point where we will start downloading the tiles

    start_point_lng = bbox_coords[0]  # getting the starting lat lng
    start_point_lat = bbox_coords[1]

    # end point where we should stop downloading the tile
    end_point_lng = bbox_coords[2]  # getting the ending lat lng
    end_point_lat = bbox_coords[3]

    # Note :  lat=y-axis, lng=x-axis
    # getting tile coordinate for first point of bbox
    start_x, start_y = latlng2tile(
        zoom=zm_level,
        lat=start_point_lat,
        lng=start_point_lng,
        tile_size=tile_size,
    )
    start = [start_x, start_y]

    # getting tile coordinate for last point of bbox
    end_x, end_y = latlng2tile(
        zoom=zm_level,
        lat=end_point_lat,
        lng=end_point_lng,
        tile_size=tile_size,
    )
    end = [end_x, end_y]
    return start, end


def tms2img(start: list, end: list, zm_level, base_path, source="maxar"):
    """Downloads imagery from start to end tile coordinate system

    DEPRECATED: This function is deprecated. Use geoml_toolkits.download_tiles() instead.
    This wrapper is maintained for backward compatibility.

    Args:
        start (list):[tile_x,tile_y]
        end (list): [tile_x,tile_y],
        source (string): it should be either url string or maxar value
        zm_level : Zoom level
        base_path : Source where image will be downloaded
    """
    import warnings
    warnings.warn(
        "tms2img is deprecated. Use 'from geoml_toolkits import download_tiles' instead.",
        DeprecationWarning,
        stacklevel=2
    )

    try:
        from geoml_toolkits import download_tiles, TileSource

        # Convert start/end coordinates to bbox
        # Note: This is a simplified conversion - the original function had complex logic
        # For full compatibility, users should migrate to geoml_toolkits directly

        # Create TileSource based on source parameter
        if source == "maxar":
            connect_id = os.environ.get("MAXAR_CONNECT_ID")
            if not connect_id:
                raise ValueError("MAXAR_CONNECT_ID environment variable is required for Maxar source")

            tile_source = TileSource(
                name="maxar",
                url=f"https://services.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe:ImageryTileService@EPSG:3857@jpg/{{z}}/{{x}}/{{y}}.jpg?connectId={connect_id}&flipy=true",
                scheme="xyz"
            )
        else:
            # Assume source is a URL template
            tile_source = TileSource(
                name="custom",
                url=source,
                scheme="xyz"
            )

        # Convert tile coordinates to approximate bbox
        # This is a simplified conversion - for exact behavior, use geoml_toolkits directly
        import mercantile

        # Get bounds for the tile range
        west_tile = mercantile.Tile(start[0], start[1], zm_level)
        east_tile = mercantile.Tile(end[0], end[1], zm_level)

        west_bounds = mercantile.bounds(west_tile)
        east_bounds = mercantile.bounds(east_tile)

        bbox = [
            min(west_bounds.west, east_bounds.west),
            min(west_bounds.south, east_bounds.south),
            max(west_bounds.east, east_bounds.east),
            max(west_bounds.north, east_bounds.north)
        ]

        # Use geoml_toolkits download_tiles function
        import asyncio

        async def download_wrapper():
            return await download_tiles(
                tms=tile_source,
                zoom=zm_level,
                bbox=bbox,
                output_dir=base_path,
                georeference=True
            )

        # Run the async function
        return asyncio.run(download_wrapper())

    except ImportError:
        # Fallback to original implementation if geoml_toolkits is not available
        print("Warning: geoml_toolkits not available, using legacy implementation")
        _legacy_tms2img(start, end, zm_level, base_path, source)


def _legacy_tms2img(start: list, end: list, zm_level, base_path, source="maxar"):
    """Legacy implementation of tms2img for backward compatibility."""

    def download_image(url, base_path, source_name):
        response = requests.get(url)
        image = response.content

        url_splitted_list = url.split("/")
        filename = f"{base_path}/{source_name}-{url_splitted_list[-2]}-{url_splitted_list[-1]}-{url_splitted_list[-3]}.png"

        with open(filename, "wb") as f:
            f.write(image)

    begin_x = start[0]
    begin_y = start[1]
    stop_x = end[0]
    stop_y = end[1]

    print(f"Download starting from {start} to {end} using source {source} - {zm_level}")

    start_x = begin_x
    start_y = begin_y
    source_name = "OAM"
    download_urls = []

    while start_x <= stop_x:
        start_y = begin_y
        while start_y >= stop_y:
            download_path = [start_x, start_y]
            if source == "maxar":
                try:
                    connect_id = os.environ.get("MAXAR_CONNECT_ID")
                except Exception as ex:
                    raise ex
                source_name = source
                download_url = f"https://services.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe:ImageryTileService@EPSG:3857@jpg/{zm_level}/{download_path[0]}/{download_path[1]}.jpg?connectId={connect_id}&flipy=true"
            else:
                download_url = source.format(
                    x=download_path[0], y=download_path[1], z=zm_level
                )
            download_urls.append(download_url)
            start_y = start_y - 1
        start_x = start_x + 1

    # Use the ThreadPoolExecutor to download the images in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for url in download_urls:
            executor.submit(download_image, url, base_path, source_name)


def fetch_osm_data(payload: json, API_URL="https://api-prod.raw-data.hotosm.org/v1"):
    """
    DEPRECATED: This function is deprecated. Use geoml_toolkits.download_osm_data() instead.
    This wrapper is maintained for backward compatibility.

    args :
        payload : Payload request for API URL
        API_URL : Raw data API URL
    Returns :
        geojson
    """
    import warnings
    warnings.warn(
        "fetch_osm_data is deprecated. Use 'from geoml_toolkits import download_osm_data' instead.",
        DeprecationWarning,
        stacklevel=2
    )

    try:
        from geoml_toolkits import download_osm_data

        # Try to extract parameters from payload for the new function
        # This is a best-effort conversion - for full functionality, use geoml_toolkits directly

        if 'geometry' in payload:
            # Extract bbox from geometry if possible
            geometry = payload['geometry']
            if geometry.get('type') == 'Polygon':
                coords = geometry['coordinates'][0]
                lons = [coord[0] for coord in coords]
                lats = [coord[1] for coord in coords]
                bbox = [min(lons), min(lats), max(lons), max(lats)]
            else:
                raise ValueError("Only Polygon geometry is supported in this compatibility wrapper")
        else:
            raise ValueError("Payload must contain 'geometry' field")

        # Extract other parameters
        feature_type = payload.get('filters', {}).get('tags', {}).get('building', 'yes')
        if feature_type == 'yes':
            feature_type = 'building'

        # Use geoml_toolkits download_osm_data function
        import asyncio

        async def download_wrapper():
            return await download_osm_data(
                bbox=bbox,
                feature_type=feature_type,
                api_url=API_URL
            )

        # Run the async function and return the result
        return asyncio.run(download_wrapper())

    except ImportError:
        # Fallback to original implementation if geoml_toolkits is not available
        print("Warning: geoml_toolkits not available, using legacy implementation")
        return _legacy_fetch_osm_data(payload, API_URL)


def _legacy_fetch_osm_data(payload: json, API_URL="https://api-prod.raw-data.hotosm.org/v1"):
    """Legacy implementation of fetch_osm_data for backward compatibility."""
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    task_response = requests.post(
        url=f"{API_URL}/snapshot/", data=json.dumps(payload), headers=headers
    )

    task_response.raise_for_status()
    result = task_response.json()
    print(result)
    task_track_url = result["track_link"]
    stop_loop = False
    while not stop_loop:
        check_result = requests.get(url=f"{API_URL}{task_track_url}")
        check_result.raise_for_status()
        res = (
            check_result.json()
        )  # status will tell current status of your task after it turns to success it will give result
        if res["status"] == "SUCCESS" or res["status"] == "FAILED":
            stop_loop = True
        time.sleep(1)  # check each second
    # Download the zip file from the URL
    url = res["result"]["download_url"]
    response = urllib.request.urlopen(url)

    # Open the zip file from the response data
    with zipfile.ZipFile(io.BytesIO(response.read()), "r") as zip_ref:
        with zip_ref.open("Export.geojson") as file:
            my_export_geojson = json.loads(file.read())
    return my_export_geojson


# Third party imports
import matplotlib.pyplot as plt
import pandas as pd


def compute_iou_chart_from_yolo_results(results_csv_path, results_output_chart_path):

    data = pd.read_csv(results_csv_path)

    data["IoU(M)"] = 1 / (
        1 / data["metrics/precision(M)"] + 1 / data["metrics/recall(M)"] - 1
    )
    chart = data.plot(
        x="epoch",
        y="IoU(M)",
        title="IoU (Mask) per Epoch",
        xticks=data["epoch"].astype(int),
    ).get_figure()

    chart.savefig(results_output_chart_path)
    return results_output_chart_path


def get_yolo_iou_metrics(model_path):

    model_val = ultralytics.YOLO(model_path)
    model_val_metrics = (
        model_val.val().results_dict
    )  ### B and M denotes bounding box and mask respectively
    # print(metrics)
    iou_accuracy = 1 / (
        1 / model_val_metrics["metrics/precision(M)"]
        + 1 / model_val_metrics["metrics/recall(M)"]
        - 1
    )  # ref here https://github.com/ultralytics/ultralytics/issues/9984#issuecomment-2422551315
    final_accuracy = iou_accuracy * 100
    del model_val  # release model reference
    gc.collect()   # trigger cleanup of file handles
    return final_accuracy


def export_model_to_onnx(model_path):
    model = ultralytics.YOLO(model_path)
    model.export(format="onnx", imgsz=[256, 256])
    # model.export(format='tflite')
    del model  # release model reference
    gc.collect()
    return True



def check4checkpoint(name, weights, output_path, remove_old=False):
    ckpt = os.path.join(
        os.path.join(output_path, "checkpoints"), name, "weights", "last.pt"
    )
    if os.path.exists(ckpt):
        if remove_old:
            os.remove(ckpt)
            print(f"Removed old checkpoint {ckpt}")
            return weights, False
        print(f"Set weights to {ckpt}")
        return ckpt, True
    return weights, False


def get_tiles(zoom, geojson=None, bbox=None, within=False):
    """
    Get tiles for a given zoom level and area of interest.

    Args:
        zoom: Zoom level
        geojson: GeoJSON file path, string, or dictionary
        bbox: Bounding box coordinates [xmin, ymin, xmax, ymax]
        within: Whether to get only tiles completely within the geometry

    Returns:
        List of mercantile.Tile objects
    """
    if geojson is not None:
        geometry = get_geometry(geojson, None)
    elif bbox is not None:
        geometry = get_geometry(None, bbox)
    else:
        raise ValueError("Either geojson or bbox must be provided")

    # Get tiles for the geometry
    if within:
        tiles = list(mercantile.tiles(*geometry['coordinates'][0][0], zoom))
    else:
        # Get bounding box of geometry
        if geometry['type'] == 'Polygon':
            coords = geometry['coordinates'][0]
        else:
            # For other geometry types, get bounds
            import shapely.geometry
            geom = shapely.geometry.shape(geometry)
            bounds = geom.bounds
            coords = [[bounds[0], bounds[1]], [bounds[2], bounds[3]]]

        # Get all coordinates to find bounds
        lons = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]

        west, south, east, north = min(lons), min(lats), max(lons), max(lats)
        tiles = list(mercantile.tiles(west, south, east, north, zoom))

    return tiles


def get_geometry(geojson=None, bbox=None):
    """
    Get geometry from either geojson or bbox.

    Args:
        geojson: GeoJSON file path, string, or dictionary
        bbox: Bounding box coordinates [xmin, ymin, xmax, ymax]

    Returns:
        GeoJSON geometry dictionary
    """
    if geojson is not None:
        if isinstance(geojson, str):
            if os.path.exists(geojson):
                import geopandas as gpd
                gdf = gpd.read_file(geojson)
                # Union all geometries and get the first one
                geom = gdf.geometry.unary_union
                if hasattr(geom, '__geo_interface__'):
                    return geom.__geo_interface__
                else:
                    return geom
            else:
                try:
                    geojson_data = json.loads(geojson)
                    if 'features' in geojson_data:
                        # Return the first feature's geometry
                        return geojson_data['features'][0]['geometry']
                    else:
                        return geojson_data
                except json.JSONDecodeError:
                    raise ValueError("Invalid GeoJSON string")
        else:
            # Assume it's already a dictionary
            if 'features' in geojson:
                return geojson['features'][0]['geometry']
            else:
                return geojson
    elif bbox is not None:
        # Create a polygon from bbox
        xmin, ymin, xmax, ymax = bbox
        return {
            "type": "Polygon",
            "coordinates": [[
                [xmin, ymin],
                [xmax, ymin],
                [xmax, ymax],
                [xmin, ymax],
                [xmin, ymin]
            ]]
        }
    else:
        raise ValueError("Either geojson or bbox must be provided")


def split_geojson_by_tiles(geojson_path, tiles_geojson, output_dir, prefix="OAM"):
    """
    Split a GeoJSON file by tiles.

    Args:
        geojson_path: Path to the GeoJSON file to split
        tiles_geojson: GeoJSON containing tile geometries
        output_dir: Output directory for split files
        prefix: Prefix for output files
    """
    import geopandas as gpd

    # Read the main GeoJSON
    main_gdf = gpd.read_file(geojson_path)

    # Read tiles GeoJSON
    if isinstance(tiles_geojson, str):
        if os.path.exists(tiles_geojson):
            tiles_gdf = gpd.read_file(tiles_geojson)
        else:
            # Parse as JSON string
            tiles_data = json.loads(tiles_geojson)
            tiles_gdf = gpd.GeoDataFrame.from_features(tiles_data['features'])
    else:
        tiles_gdf = gpd.GeoDataFrame.from_features(tiles_geojson['features'])

    # Ensure same CRS
    if main_gdf.crs != tiles_gdf.crs:
        tiles_gdf = tiles_gdf.to_crs(main_gdf.crs)

    # Split by each tile
    for idx, tile_row in tiles_gdf.iterrows():
        tile_geom = tile_row.geometry

        # Find intersecting features
        intersecting = main_gdf[main_gdf.intersects(tile_geom)]

        if not intersecting.empty:
            # Create output filename based on tile properties or index
            output_filename = f"{prefix}-tile-{idx}.geojson"
            output_path = os.path.join(output_dir, output_filename)

            # Save intersecting features
            intersecting.to_file(output_path, driver="GeoJSON")


def merge_rasters(input_dir, output_path):
    """
    Merge all raster files in a directory into a single raster.

    Args:
        input_dir: Directory containing raster files
        output_path: Path for the merged output raster
    """
    # Find all raster files
    raster_files = []
    for ext in ['*.tif', '*.tiff', '*.png', '*.jpg', '*.jpeg']:
        raster_files.extend(glob(os.path.join(input_dir, ext)))

    if not raster_files:
        raise ValueError(f"No raster files found in {input_dir}")

    # Open all raster files
    src_files_to_mosaic = []
    for file in raster_files:
        src = rasterio.open(file)
        src_files_to_mosaic.append(src)

    # Merge rasters
    mosaic, out_trans = merge(src_files_to_mosaic)

    # Update metadata
    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "crs": src_files_to_mosaic[0].crs
    })

    # Write merged raster
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    # Close all source files
    for src in src_files_to_mosaic:
        src.close()

    print(f"Merged {len(raster_files)} rasters into {output_path}")