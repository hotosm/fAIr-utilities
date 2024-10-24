# Standard library imports
import argparse
import os
from pathlib import Path

# Third party imports
import torch
import ultralytics

# Reader imports
from hot_fair_utilities.model.yolo import YOLOSegWithPosWeight

ROOT = Path(__file__).parent.absolute()
DATA_ROOT = str(ROOT / "ramp-training")
LOGS_ROOT = str(ROOT / "checkpoints")


#
# Different hyperparameters from default in YOLOv8 release models
# https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/default.yaml
#

HYPERPARAM_CHANGES = {
    "imgsz": 256,
    "mosaic": 0.0,
    "overlap_mask": False,
    "cls": 0.5,
    "degrees": 30.0,
    # "optimizer": "SGD",
    # "weight_decay": 0.001,
}


# torch.set_float32_matmul_precision("high")


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=str, default="0", help="GPU id")
    parser.add_argument(
        "--data",
        type=str,
        default=os.path.join(DATA_ROOT),
        help="Directory containing diractory 'yolo' with dataset.yaml.",
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
        project=LOGS_ROOT,
        name=name,
        epochs=int(epochs),
        resume=resume,
        deterministic=False,
        device=[int(i) for i in gpu.split(",")] if "," in gpu else gpu,
        **kwargs,
    )
    return weights


def check4checkpoint(name, weights):
    ckpt = os.path.join(LOGS_ROOT, name, "weights", "best.pt")
    if os.path.exists(ckpt):
        print(f"Set weights to {ckpt}")
        return ckpt, True
    return weights, False


if __name__ == "__main__":
    main()
