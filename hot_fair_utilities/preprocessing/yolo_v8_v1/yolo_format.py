# Standard library imports
import concurrent.futures
import random
import traceback
import warnings
from pathlib import Path

# Third party imports
import cv2
import numpy as np
import rasterio
import yaml

# Mask types from https://rampml.global/data-preparation/
CLASS_NAMES = ["footprint", "boundary", "contact"]


def yolo_format(
    preprocessed_dirs, yolo_dir, val_dirs=None, multimask=False, p_val=None
):
    """
    Creates ultralytics YOLOv5 format dataset from RAMP preprocessed data.
    Supports either single data directory or multiple directories.
    For multiple directories, data can be split to train, val.
    Dataset can be inspected using fiftyone, see
    https://docs.voxel51.com/user_guide/dataset_creation/datasets.html#yolov5dataset

    Args:
        preprocessed_dirs (any): Path or list of paths containing
            directories: "chips", "binarymasks" or "multimasks" from RAMP preprocessing phase.
        yolo_dir (str): Path where YOLO data will be stored.
        val_dirs (list, optional): List of paths from preprocessed_dirs that will be added to validation set
            instead of training set.
        multimask (bool, optional): If true, multimasks are used instead of binarymasks.
        p_val (float, optional): Float in [0,1] specifying the probability of an image being added to val.
            If val_dirs is set, this option has no effect.

    Examples:
        yolo_format("ramp_sample_1", "yolo")
        yolo_format(["ramp_sample_1", "ramp_sample_2"], "yolo")
        yolo_format(["ramp_sample_1"], "yolo", ["ramp_sample_2"])
    """
    classes = [1, 2, 3] if multimask else [1]
    if isinstance(preprocessed_dirs, str):
        preprocessed_dirs = [preprocessed_dirs]
    if val_dirs is not None:
        preprocessed_dirs = list(set(preprocessed_dirs) - set(val_dirs))
        p_val = None
    else:
        val_dirs = []
    preprocessed_dirs, yolo_dir = [Path(x) for x in preprocessed_dirs], Path(yolo_dir)
    val_dirs = [Path(x) for x in val_dirs]
    mask_dirname = Path("multimasks") if multimask else Path("binarymasks")

    preprocessed_dirs_stems = [x.stem for x in preprocessed_dirs]
    val_dirs_stems = [x.stem for x in val_dirs] if val_dirs is not None else []
    yolo_dir_suffixes = ["_train", "_val"] if p_val else [""]

    # Save image symlinks and labels
    for dname, dname_stem in zip(
        preprocessed_dirs + val_dirs, preprocessed_dirs_stems + val_dirs_stems
    ):
        img_dir = dname / "chips" if (dname / "chips").is_dir() else dname / "source"
        mask_dir = dname / mask_dirname
        yolo_img_dir, yolo_label_dir = (
            yolo_dir / "images" / dname_stem,
            yolo_dir / "labels" / dname_stem,
        )

        for dir in [yolo_img_dir, yolo_label_dir]:
            for suf in yolo_dir_suffixes:
                Path(str(dir) + suf).mkdir(parents=True, exist_ok=True)

        files = list(img_dir.iterdir())
        random.shuffle(files)
        _image_iteration(
            files[0],
            img_dir,
            mask_dir,
            yolo_img_dir,
            yolo_label_dir,
            classes,
            1.0 if p_val else None,
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(
                lambda x: __image_iteration_func(
                    x, img_dir, mask_dir, yolo_img_dir, yolo_label_dir, classes, p_val
                ),
                files[1:],
            )

    if p_val:
        val_dirs_stems = [str(p) + "_val" for p in preprocessed_dirs_stems]
        preprocessed_dirs_stems = [str(p) + "_train" for p in preprocessed_dirs_stems]

    # Save yolo_dataset.yaml
    dataset = {
        "names": {i - 1: name for i, name in zip(classes, CLASS_NAMES[: len(classes)])},
        "path": str(yolo_dir.absolute()),
        "train": (
            f"./images/{str(preprocessed_dirs_stems[0])}/"
            if len(preprocessed_dirs) == 1
            else [f"./images/{str(d)}" for d in preprocessed_dirs_stems]
        ),
    }
    if len(val_dirs_stems) > 0:
        dataset["val"] = (
            f"./images/{str(val_dirs_stems[0])}/"
            if len(val_dirs_stems) == 1
            else [f"./images/{str(d)}" for d in val_dirs_stems]
        )
    with open(yolo_dir / "yolo_dataset.yaml", "w") as handle:
        yaml.dump(dataset, handle, default_flow_style=False)


def _image_iteration(
    img, img_dir, mask_dir, yolo_img_dir, yolo_label_dir, classes, p_val
):
    if p_val:
        if random.uniform(0, 1) > p_val:
            yolo_img_dir = Path(str(yolo_img_dir) + "_train")
            yolo_label_dir = Path(str(yolo_label_dir) + "_train")
        else:
            yolo_img_dir = Path(str(yolo_img_dir) + "_val")
            yolo_label_dir = Path(str(yolo_label_dir) + "_val")

    img = img.name
    mask = Path(str(img)[:-4] + ".mask.tif")
    assert (mask_dir / mask).exists(), f"{img} does not have its {mask} in {mask_dir}"

    # Image -> symlink
    if not (yolo_img_dir / img).is_symlink():
        (yolo_img_dir / img).symlink_to(img_dir / img)

    # Mask -> find contour points, write them to txt
    with rasterio.open(str(mask_dir / mask)) as handle:
        data = handle.read()
    h, w = data.shape[1:]
    label = str(img)[:-4] + ".txt"
    with open(yolo_label_dir / label, "w") as handle:
        for cls in classes:
            x = np.where(data == cls, 255, 0).squeeze().astype("uint8")
            contours, _ = cv2.findContours(
                x, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_TC89_KCOS
            )
            for contour in contours:  # contour (n, 1, 2)
                if contour.shape[0] > 2:  # at least 3-point polygon
                    contour = contour / [w, h]
                    line = f"{cls - 1} {' '.join([str(c) for c in contour.flatten().tolist()])}\n"
                    handle.write(line)


def __image_iteration_func(
    img, img_dir, mask_dir, yolo_img_dir, yolo_label_dir, classes, p_val
):
    try:
        _image_iteration(
            img, img_dir, mask_dir, yolo_img_dir, yolo_label_dir, classes, p_val
        )
    except Exception as e:
        full_trace = "\n" + " ".join(traceback.format_exception(e))
        warnings.warn(f"Image {img.name} caused {full_trace}")


if __name__ == "__main__":
    random.seed(0)
    # root = "/tf/ramp-data/sample_119"
    root = "/home/powmol/wip/hotosm/fAIr-utilities/ramp-data/sample_119"
    yolo_format([root + "/preprocessed"], root + "/yolo", multimask=False, p_val=0.05)
