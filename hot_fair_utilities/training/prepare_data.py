# Import the exec function
from __future__ import print_function

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path
from shutil import copytree, rmtree


class RaiseError(Exception):
    def __init__(self, message):
        self.message = message


def split_training_2_validation(input_path, output_path):
    """Converts training 2 validation

    Currently supported for ramp , It converts training dataset provided by preprocessing script to validation datastes reuqired by ramp
    """

    RAMP_HOME = os.environ["RAMP_HOME"]
    PYTHON_HOME = os.environ.get("PYTHON_HOME")
    python_exec = "python"
    if PYTHON_HOME:
        python_exec = PYTHON_HOME

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
    try:
        subprocess.check_output(
            [
                python_exec,
                f"{RAMP_HOME}/ramp-code/scripts/make_train_val_split_lists.py",
                "-src",
                f"{dst_path}/chips",
                "-pfx",
                f"{dst_path}/fair_split",
                "-trn",
                "0.85",
                "-val",
                "0.15",
            ],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as ex:
        raise RaiseError(ex.output.decode())

    # move all the VALIDATION chips, labels and masks to their new locations
    try:
        subprocess.check_output(
            [
                python_exec,
                f"{RAMP_HOME}/ramp-code/scripts/move_chips_from_csv.py",
                "-sd",
                f"{dst_path}/chips",
                "-td",
                f"{dst_path}/val-chips",
                "-csv",
                f"{dst_path}/fair_split_val.csv",
                "-mv",
            ],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as ex:
        raise RaiseError(ex.output.decode())
    try:
        subprocess.check_output(
            [
                python_exec,
                f"{RAMP_HOME}/ramp-code/scripts/move_chips_from_csv.py",
                "-sd",
                f"{dst_path}/labels",
                "-td",
                f"{dst_path}/val-labels",
                "-csv",
                f"{dst_path}/fair_split_val.csv",
                "-mv",
            ],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as ex:
        raise RaiseError(ex.output.decode())

    try:
        subprocess.check_output(
            [
                python_exec,
                f"{RAMP_HOME}/ramp-code/scripts/move_chips_from_csv.py",
                "-sd",
                f"{dst_path}/binarymasks",
                "-td",
                f"{dst_path}/val-binarymasks",
                "-csv",
                f"{dst_path}/fair_split_val.csv",
                "-mv",
            ],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as ex:
        raise RaiseError(ex.output.decode())
