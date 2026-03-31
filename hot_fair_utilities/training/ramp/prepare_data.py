# Import the exec function

# Standard library imports
import csv
import os
import random
from pathlib import Path
from shutil import copytree, move, rmtree


class RaiseError(Exception):
    def __init__(self, message):
        self.message = message


def _normalize_sample_stem(file_name: str) -> str:
    sample_stem = Path(file_name).stem
    if sample_stem.endswith(".mask"):
        return sample_stem[: -len(".mask")]
    return sample_stem


def _write_split_csv(csv_path: Path, filenames: list[str]) -> None:
    with csv_path.open("w", newline="") as file_handle:
        writer = csv.writer(file_handle)
        for filename in filenames:
            writer.writerow([filename])


def _split_filenames(chips_dir: Path, train_ratio: float, random_seed: int = 42) -> tuple[list[str], list[str]]:
    if not chips_dir.exists():
        raise RaiseError(f"Chips directory does not exist: {chips_dir}")

    filenames = sorted(file.name for file in chips_dir.iterdir() if file.is_file())
    if not filenames:
        raise RaiseError(f"No chip files found in: {chips_dir}")

    random_generator = random.Random(random_seed)
    random_generator.shuffle(filenames)

    train_count = int(len(filenames) * train_ratio)
    train_filenames = sorted(filenames[:train_count])
    val_filenames = sorted(filenames[train_count:])
    return train_filenames, val_filenames


def _move_files_for_validation(source_dir: Path, target_dir: Path, val_filenames: list[str]) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    val_stems = {_normalize_sample_stem(filename) for filename in val_filenames}
    for source_file in source_dir.iterdir():
        if not source_file.is_file():
            continue
        if _normalize_sample_stem(source_file.name) not in val_stems:
            continue
        move(str(source_file), str(target_dir / source_file.name))


def split_training_2_validation(input_path, output_path, multimasks=False):
    """Split training data into training and validation sets for ramp."""

    # Define the source and destination paths
    src_path = input_path
    dst_path = output_path

    # Check if the path exists
    if os.path.exists(dst_path):
        # Delete the directory and its contents
        rmtree(dst_path)
    # Use the copytree function to copy the source directory and its contents to the destination directory
    copytree(src_path, dst_path)

    destination_path = Path(dst_path)
    chips_dir = destination_path / "chips"
    train_filenames, val_filenames = _split_filenames(chips_dir, train_ratio=0.85)

    _write_split_csv(destination_path / "fair_split_train.csv", train_filenames)
    _write_split_csv(destination_path / "fair_split_val.csv", val_filenames)

    _move_files_for_validation(destination_path / "chips", destination_path / "val-chips", val_filenames)
    _move_files_for_validation(destination_path / "labels", destination_path / "val-labels", val_filenames)

    if multimasks:
        source_masks_dir = destination_path / "multimasks"
        target_masks_dir = destination_path / "val-multimasks"
    else:
        source_masks_dir = destination_path / "binarymasks"
        target_masks_dir = destination_path / "val-binarymasks"
    _move_files_for_validation(source_masks_dir, target_masks_dir, val_filenames)
