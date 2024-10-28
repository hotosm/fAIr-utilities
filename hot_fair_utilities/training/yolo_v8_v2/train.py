# Standard library imports
import argparse
import os
from pathlib import Path

# Third party imports
import torch
import ultralytics

# Reader imports
from hot_fair_utilities.model.yolo import YOLOSegWithPosWeight

ROOT = Path(os.getenv("YOLO_ROOT", Path(__file__).parent.absolute()))
DATA_ROOT = str(Path(os.getenv("YOLO_DATA_ROOT", ROOT / "yolo-training")))
LOGS_ROOT = str(Path(os.getenv("YOLO_LOGS_ROOT", ROOT / "checkpoints")))


HYPERPARAM_CHANGES = {
    "amp": True,
    # lr setup
    "optimizer": "auto",
    "lr0": 0.00854,
    "lrf": 0.01232,
    "momentum": 0.95275,
    "weight_decay": 0.00058,
    "warmup_epochs": 3.82177,
    "warmup_momentum": 0.81423,
    # loss parameters
    "box": 7.48109,
    "cls": 0.775,
    "dfl": 1.5,
    # aug use
    "hsv_h": 0.01269,
    "hsv_s": 0.68143,
    "hsv_v": 0.27,
    # aug turn off
    "mosaic": 0,
    "translate": 0,
    "scale": 0,
    "shear": 0,
    "flipud": 0.5,
    "fliplr": 0.255,
    "erasing": 0,
    "degrees": 15.75,
    # Add other parameters as needed
    "overlap_mask": False,
    "nbs": 64,
    "plots": True,
    "cache": True,
    "val": True,
    "save": True,
}


def train(data, weights, gpu, epochs, batch_size, pc, output_path=None):
    back = (
        "n"
        if "yolov8n" in weights
        else "s" if "yolov8s" in weights else "m" if "yolov8m" in weights else "?"
    )
    data_scn = str(Path(data) / "yolo" / "dataset.yaml")
    dataset = data_scn.split("/")[-3]
    kwargs = HYPERPARAM_CHANGES
    print(f"Backbone: {back}, Dataset: {dataset}, Epochs: {epochs}")

    name = f"yolov8{back}-seg_{dataset}_ep{epochs}_bs{batch_size}"
    if output_path:
        name = output_path
    if float(pc) != 0.0:
        name += f"_pc{pc}"
        kwargs = {**kwargs, "pc": pc}
        yolo = YOLOSegWithPosWeight
    else:
        yolo = ultralytics.YOLO

    weights, resume = check4checkpoint(name, weights)
    model = yolo(weights)
    model.train(
        data=data_scn,
        project=LOGS_ROOT,  # Using the environment variable with fallback
        name=name,
        epochs=int(epochs),
        resume=resume,
        deterministic=False,
        device=[int(i) for i in gpu.split(",")] if "," in gpu else gpu,
        **kwargs,
    )
    return weights


def check4checkpoint(name, weights):
    ckpt = os.path.join(LOGS_ROOT, name, "weights", "last.pt")
    if os.path.exists(ckpt):
        print(f"Set weights to {ckpt}")
        return ckpt, True
    return weights, False
