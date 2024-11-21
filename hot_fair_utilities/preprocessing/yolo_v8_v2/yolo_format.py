# Standard library imports
import glob
import os

# Third party imports
import numpy as np
import yaml
from tqdm import tqdm
import shutil
from .utils import convert_tif_to_jpg, write_yolo_file


def yolo_format(
    input_path="preprocessed/*",
    output_path="ramp_data_yolo",
    seed=42,
    train_split=0.7,
    val_split=0.15,
    test_split=0.15,
):
    """
    Preprocess data for YOLO model training.

    Args:
        input_path (str, optional): The path to the input data folders. Defaults to "preprocessed/*".
        output_path (str, optional): The path to the output YOLO data folders. Defaults to "ramp_data_yolo".
        seed (int, optional): The random seed for data splitting. Defaults to 42.
        train_split (float, optional): The percentage of data to be used for training. Defaults to 0.7.
        val_split (float, optional): The percentage of data to be used for validation. Defaults to 0.15.
        test_split (float, optional): The percentage of data to be used for testing. Defaults to 0.15.

    Returns:
        None
    """
    # Verify the sum of the splits
    assert (
        train_split + val_split + test_split == 1
    ), "The sum of the splits must be equal to 1"

    print(f"Train-val-test split: {train_split}-{val_split}-{test_split}")

    # Set the random seed
    np.random.seed(seed)

    # Find the files
    cwps, lwps, base_folders = find_files(input_path)

    # Shuffle indices
    shuffled_indices = np.random.permutation(len(cwps))

    # Calculate split indices
    train_end = int(len(cwps) * train_split)
    val_end = train_end + int(len(cwps) * val_split)

    # Split the indices into training, validation, and testing
    train_indices = shuffled_indices[:train_end]
    val_indices = shuffled_indices[train_end:val_end]
    test_indices = shuffled_indices[val_end:]

    # Create train, val, and test arrays
    train_cwps = [cwps[i] for i in train_indices]
    val_cwps = [cwps[i] for i in val_indices]
    test_cwps = [cwps[i] for i in test_indices]

    # Output the results to verify
    print(f"\nTrain array size: {len(train_cwps)}")
    print(f"Validation array size: {len(val_cwps)}")
    print(f"Test array size: {len(test_cwps)}\n")

    # Check if the YOLO folder exists, if not create labels, images, and folders
    if  os.path.exists(output_path):
        shutil.rmtree(output_path)

    os.makedirs(output_path)

    # Write the YOLO label files for the training set
    print("Generating training labels")
    for train_cwp in tqdm(train_cwps):
        write_yolo_file(train_cwp, "train", output_path)

    # Write the YOLO label files for the validation set
    print("Generating validation labels")
    for val_cwp in tqdm(val_cwps):
        write_yolo_file(val_cwp, "val", output_path)

    # Write the YOLO label files for the test set
    print("Generating test labels")
    for test_cwp in tqdm(test_cwps):
        write_yolo_file(test_cwp, "test", output_path)

    # Convert the chip files to JPEG format
    print("Generating training images")
    for train_cwp in tqdm(train_cwps):
        convert_tif_to_jpg(train_cwp, "train", output_path)

    print("Generating validation images")
    for val_cwp in tqdm(val_cwps):
        convert_tif_to_jpg(val_cwp, "val", output_path)

    print("Generating test images")
    for test_cwp in tqdm(test_cwps):
        convert_tif_to_jpg(test_cwp, "test", output_path)

    attr = {
        "path": output_path,
        "train": "images/train",
        "val": "images/val",
        "names": {0: 1},
    }
    # os.makedirs(os.path.join(output_path, "yolo"), exist_ok=True)

    YAML_PATH = os.path.join(output_path, "yolo_dataset.yaml")
    print(f"Writing the data file with path={YAML_PATH}")
    # Write the file
    with open(YAML_PATH, "w") as f:
        yaml.dump(attr, f)



def find_files(data_folders):
    """
    Find chip (.tif) and label (.geojson) files in the specified folders.

    Args:
        data_folders (str): The path to the input data folders.

    Returns:
        cwps (list): List of chip filenames with path.
        lwps (list): List of label filenames with path.
        base_folders (list): List of base folder names.
    """
    # Find the folders
    data_folders = glob.glob(data_folders)

    # Create a list to store chip (.tif), mask (.mask.tif), and label (.geojson) filenames with path
    cwps = []
    lwps = []

    # Create a list to store the base folder names
    base_folders = []

    for folder in data_folders:
        # Pattern to match all .tif files in the current folder, including subdirectories
        tif_pattern = f"{folder}/chips/*.tif"

        # Find all .tif files in the current 'training*' folder and its subdirectories
        found_tif_files = glob.glob(tif_pattern, recursive=True)

        # Filter out .mask.tif files and add the rest to the tif_files list
        for file in found_tif_files:
            if file.endswith(".tif"):
                cwps.append(file)

        # Pattern to match all .geojson files in the current folder, including subdirectories
        geojson_pattern = f"{folder}/labels/*.geojson"

        # Find all .geojson files
        found_geojson_files = glob.glob(geojson_pattern, recursive=True)

        # Add found .geojson files to the geojson_files list
        lwps.extend(found_geojson_files)

    # Sort the lists
    cwps.sort()
    lwps.sort()

    # Assert that the the number files for each type are the same
    assert len(cwps) == len(
        lwps
    ), f"Number of {len(cwps)} tif files and {len(lwps) }label files do not match"

    # Function to check that the filenames match
    for n, cwp in enumerate(cwps):
        c = os.path.basename(cwp).replace(".tif", "")
        l = os.path.basename(lwps[n]).replace(".geojson", "")

        assert c == l, f"Chip and label filenames do not match: {c} != {l}"

        base_folders.append(cwp.split("/")[1])

    return cwps, lwps, base_folders
