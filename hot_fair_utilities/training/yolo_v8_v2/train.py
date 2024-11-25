# Standard library imports
import argparse
import os
from pathlib import Path

# Third party imports
import torch
import ultralytics
from ...utils import get_yolo_iou_metrics,compute_iou_chart_from_yolo_results,export_model_to_onnx
# Reader imports
from hot_fair_utilities.model.yolo import YOLOSegWithPosWeight

# ROOT = Path(os.getenv("YOLO_ROOT", Path(__file__).parent.absolute()))
# DATA_ROOT = str(Path(os.getenv("YOLO_DATA_ROOT", ROOT / "yolo-training")))


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


def train(data, weights, epochs, batch_size, pc, output_path, dataset_yaml_path,gpu=("cuda" if torch.cuda.is_available() else "cpu"),):
    back = (
        "n"
        if "yolov8n" in weights
        else "s" if "yolov8s" in weights else "m" if "yolov8m" in weights else "?"
    )
    data_scn = dataset_yaml_path
    dataset = data_scn.split("/")[-3]
    kwargs = HYPERPARAM_CHANGES
    print(f"Backbone: {back}, Dataset: {dataset}, Epochs: {epochs}")

    name = f"yolov8{back}-seg_{dataset}_ep{epochs}_bs{batch_size}"

    if float(pc) != 0.0:
        name += f"_pc{pc}"
        kwargs = {**kwargs, "pc": pc}
        yolo = YOLOSegWithPosWeight
    else:
        yolo = ultralytics.YOLO

    weights, resume = check4checkpoint(name, weights,output_path)
    model = yolo(weights)

    model.train(
        data=data_scn,
        project=os.path.join(output_path,"checkpoints"),  # Using the environment variable with fallback
        name=name,
        epochs=int(epochs),
        resume=resume,
        verbose=True,
        deterministic=False,
        save_dir= os.path.join(output_path),
        device=[int(i) for i in gpu.split(",")] if "," in gpu else gpu,
        **kwargs,
    )

    # metrics = model.val(save_json=True, plots=True)
    # print(model.val())
    compute_iou_chart_from_yolo_results(results_csv_path=os.path.join(output_path,"checkpoints", name,'results.csv'),results_output_chart_path=os.path.join(output_path,"checkpoints", name,'iou_chart.png'))
    
    output_model_path=os.path.join(os.path.join(output_path,"checkpoints"), name, "weights", "best.pt")

    iou_model_accuracy=get_yolo_iou_metrics(output_model_path)
    export_model_to_onnx(output_model_path)

    return  output_model_path,iou_model_accuracy


def check4checkpoint(name, weights,output_path):
    ckpt = os.path.join(os.path.join(output_path,"checkpoints"), name, "weights", "last.pt")
    if os.path.exists(ckpt):
        print(f"Set weights to {ckpt}")
        return ckpt, True
    return weights, False
