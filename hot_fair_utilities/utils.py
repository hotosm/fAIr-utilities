import gc
import logging
import os
import sys
import types
from glob import glob

import pandas as pd

log = logging.getLogger(__name__)


def patch_tf_experimental_layers():
    """Patch for newer TensorFlow versions where keras.layers.experimental.preprocessing was removed.

    Ramp depends on this legacy module path. This shim redirects it to keras.layers.
    """
    import tensorflow as tf

    module = types.ModuleType("tensorflow.keras.layers.experimental")
    module.preprocessing = tf.keras.layers  # ty: ignore[unresolved-attribute]
    sys.modules["tensorflow.keras.layers.experimental"] = module


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
    model_val_metrics = model_val.val().results_dict
    precision = model_val_metrics["metrics/precision(M)"]
    recall = model_val_metrics["metrics/recall(M)"]
    iou_accuracy = 1 / (1 / precision + 1 / recall - 1)
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
            log.info("Removed old checkpoint %s", ckpt)
            return weights, False
        log.info("Set weights to %s", ckpt)
        return ckpt, True
    return weights, False
