# Import the exec function
from __future__ import print_function

# Standard library imports
import os
import subprocess
import sys
import uuid
from pathlib import Path
from shutil import copytree, rmtree


def split_training_2_validation(input_path, output_path):
    """Converts training 2 validation

    Currently supported for ramp , It converts training dataset provided by preprocessing script to validation datastes reuqired by ramp
    """

    RAMP_HOME = os.environ["RAMP_HOME"]

    sys.path.append("..")
    os.chdir(Path(RAMP_HOME))
    # output current working directory.

    # Define the source and destination paths
    src_path = input_path
    dst_path = output_path

    # Check if the path exists
    if os.path.exists(dst_path):
        # Delete the directory and its contents
        rmtree(dst_path)
    # Use the copytree function to copy the source directory and its contents to the destination directory
    copytree(src_path, dst_path)

    # Define the script as a string
    # SPLIT INTO TRAINING AND VALIDATION
    # script = f"""%run ramp-code/scripts/make_train_val_split_lists.py -src {dst_path}/chips -pfx {uid}_fair_split -trn 0.85 -val 0.15"""

    subprocess.check_call(
        [
            "python",
            "ramp-code/scripts/make_train_val_split_lists.py",
            "-src",
            f"{dst_path}/chips",
            "-pfx",
            f"{dst_path}/fair_split",
            "-trn",
            "0.85",
            "-val",
            "0.15",
        ]
    )

    # move all the VALIDATION chips, labels and masks to their new locations
    subprocess.check_call(
        [
            "python",
            "ramp-code/scripts/move_chips_from_csv.py",
            "-sd",
            f"{dst_path}/chips",
            "-td",
            f"{dst_path}/val-chips",
            "-csv",
            f"{dst_path}/fair_split_val.csv",
            "-mv",
        ]
    )
    subprocess.check_call(
        [
            "python",
            "ramp-code/scripts/move_chips_from_csv.py",
            "-sd",
            f"{dst_path}/labels",
            "-td",
            f"{dst_path}/val-labels",
            "-csv",
            f"{dst_path}/fair_split_val.csv",
            "-mv",
        ]
    )
    subprocess.check_call(
        [
            "python",
            "ramp-code/scripts/move_chips_from_csv.py",
            "-sd",
            f"{dst_path}/binarymasks",
            "-td",
            f"{dst_path}/val-binarymasks",
            "-csv",
            f"{dst_path}/fair_split_val.csv",
            "-mv",
        ]
    )
