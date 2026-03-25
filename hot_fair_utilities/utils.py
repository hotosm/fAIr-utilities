# Standard library imports
import gc
import math
import os
import re
import sys
import types
from glob import glob
from typing import Tuple

# Third party imports
import geopandas
import pandas as pd
from shapely.geometry import box

IMAGE_SIZE = 256


def patch_tf_experimental_layers():
    """Patch for newer TensorFlow versions where keras.layers.experimental.preprocessing was removed.

    Ramp depends on this legacy module path. This shim redirects it to keras.layers.
    """
    import tensorflow as tf

    module = types.ModuleType("tensorflow.keras.layers.experimental")
    setattr(module, "preprocessing", tf.keras.layers)
    sys.modules["tensorflow.keras.layers.experimental"] = module


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


def compute_iou_chart_from_yolo_results(results_csv_path, results_output_chart_path):

    data = pd.read_csv(results_csv_path)

    data["IoU(M)"] = 1 / (1 / data["metrics/precision(M)"] + 1 / data["metrics/recall(M)"] - 1)
    chart = data.plot(
        x="epoch",
        y="IoU(M)",
        title="IoU (Mask) per Epoch",
        xticks=data["epoch"].astype(int),
    ).get_figure()

    chart.savefig(results_output_chart_path)
    return results_output_chart_path


def get_yolo_iou_metrics(model_path):
    import ultralytics

    model_val = ultralytics.YOLO(model_path)
    model_val_metrics = model_val.val().results_dict  ### B and M denotes bounding box and mask respectively
    # print(metrics)
    iou_accuracy = 1 / (1 / model_val_metrics["metrics/precision(M)"] + 1 / model_val_metrics["metrics/recall(M)"] - 1)  # ref here https://github.com/ultralytics/ultralytics/issues/9984#issuecomment-2422551315
    final_accuracy = iou_accuracy * 100
    del model_val  # release model reference
    gc.collect()  # trigger cleanup of file handles
    return final_accuracy


def export_model_to_onnx(model_path):
    import ultralytics

    model = ultralytics.YOLO(model_path)
    model.export(format="onnx", imgsz=[256, 256])
    # model.export(format='tflite')
    del model  # release model reference
    gc.collect()
    return True


def check4checkpoint(name, weights, output_path, remove_old=False):
    ckpt = os.path.join(os.path.join(output_path, "checkpoints"), name, "weights", "last.pt")
    if os.path.exists(ckpt):
        if remove_old:
            os.remove(ckpt)
            print(f"Removed old checkpoint {ckpt}")
            return weights, False
        print(f"Set weights to {ckpt}")
        return ckpt, True
    return weights, False
