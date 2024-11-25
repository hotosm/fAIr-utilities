# Standard library imports
import argparse
import os
from pathlib import Path

# Third party imports
import torch
import ultralytics


# Reader imports
from hot_fair_utilities.model.yolo import YOLOSegWithPosWeight
from ...utils import compute_iou_chart_from_yolo_results, get_yolo_iou_metrics,export_model_to_onnx
# Get environment variables with fallbacks
# ROOT = Path(os.getenv("YOLO_ROOT", Path(__file__).parent.absolute()))
# DATA_ROOT = str(Path(os.getenv("YOLO_DATA_ROOT", ROOT / "yolo-training")))
# LOGS_ROOT = str(Path(os.getenv("YOLO_LOGS_ROOT", ROOT / "checkpoints")))

# Different hyperparameters from default in YOLOv8 release models
# https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/default.yaml
HYPERPARAM_CHANGES = {
    "imgsz": 256,
    "mosaic": 0.0,
    "overlap_mask": False,
    "cls": 0.5,
    "degrees": 30.0,
    "plots": True,
    # "optimizer": "SGD",
    # "weight_decay": 0.001,
}

# (weights): YOLO is trained from scratch instead of using pretrained weights of COCO dataset, because the data of drone imagery greatly differs from COCO images.
# (imgsz): image size is changed from 640 to 256, to match RAMP size.
# (mosaic): mosaic augmentations removed at all, because they did not make any sense to me to perform them on drone imagery. Mosaic augmentation can furthermore harm the final performance in some cases.
# (mask_overlap): set False, so the masks of building footprints do not overlap with masks of building edges and borders.
# (degrees): set to 30, it is an additional data augmentation that randomly rotates training images up to 30 degrees. Slightly improves the performance.
# (epochs): changed from 100 to 500. This amount better reproduces the numbers reported by ultralytics on COCO dataset for yolov8n trained from scratch (for object detection task). (Ablated.)
# (pc): new implemented option, set to 2.0, which is a weight for positive part of the classification loss, it corresponds to the `pos_weight` in BCEWithLogitsLoss. (Ablated.)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=str, default="0", help="GPU id")
    parser.add_argument(
        "--data",
        type=str,
        default=DATA_ROOT,  # Using the environment variable with fallback
        help="Directory containing directory 'yolo' with yolo_dataset.yaml.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default="yolov8n-seg.yaml",
        help="See https://docs.ultralytics.com/tasks/detect/#train",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Num of training epochs. Default is 100.",
    )
    parser.add_argument(
        "--batch-size", type=int, default=16, help="Number of images in a single batch."
    )
    parser.add_argument(
        "--pc",
        type=float,
        default=1.0,
        help="Positive weight in BCE loss. pc > 1 (pc < 1) encourages higher recall (precision)",
    )
    opt = parser.parse_args()
    return opt


def main():
    opt = parse_opt()
    os.environ["CUDA_VISIBLE_DEVICES"] = str(opt.gpu)
    print(
        f"GPU available: {torch.cuda.is_available()}, GPU count: {torch.cuda.device_count()}"
    )
    train(**vars(opt))


def train(
    data,
    weights,
    gpu=("cuda" if torch.cuda.is_available() else "cpu"),
    epochs=20,
    batch_size=8,
    pc=2.0,
    output_path=None,
    dataset_yaml_path=None,
):
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
        project=os.path.join(output_path,'checkpoints'),
        name=name,
        epochs=int(epochs),
        resume=resume,
        deterministic=False,
        verbose=True,
        save_dir= os.path.join(output_path),
        device=[int(i) for i in gpu.split(",")] if "," in gpu else gpu,
        **kwargs,
    )
    compute_iou_chart_from_yolo_results(results_csv_path=os.path.join(output_path,"checkpoints", name,'results.csv'),results_output_chart_path=os.path.join(output_path,"checkpoints", name,'iou_chart.png'))
    
    output_model_path=os.path.join(os.path.join(output_path,"checkpoints"), name, "weights", "best.pt")

    iou_model_accuracy=get_yolo_iou_metrics(output_model_path)
    export_model_to_onnx(output_model_path)

    return  output_model_path,iou_model_accuracy



def check4checkpoint(name, weights,output_path):
    ckpt = os.path.join(os.path.join(output_path,'checkpoints'), name, "weights", "last.pt")
    if os.path.exists(ckpt):
        print(f"Set weights to {ckpt}")
        return ckpt, True
    return weights, False


if __name__ == "__main__":
    main()
