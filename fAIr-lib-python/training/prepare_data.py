# Import the exec function
from __future__ import print_function

# Standard library imports
import os
import sys
import uuid
from pathlib import Path
from shutil import copytree


def split_training_2_validation(input_path):
    """Converts training 2 validation

    Currently supported for ramp , It converts training dataset provided by preprocessing script to validation datastes reuqired by ramp
    """

    RAMP_HOME = os.environ["RAMP_HOME"]

    sys.path.append("..")
    os.chdir(Path(RAMP_HOME))
    # output current working directory.
    # Note: the current working directory for this script should be 'RAMP_HOME.'
    print(os.getcwd())

    # Generate a random unique UUID , used as temp id for operation
    uid = uuid.uuid4()
    # Define the source and destination paths
    src_path = input_path
    dst_path = f"ramp-data/TRAIN/{uid}"

    # Create the destination directory if it doesn't exist
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    # Use the copytree function to copy the source directory and its contents to the destination directory
    copytree(src_path, dst_path)

    # Define the script as a string
    # SPLIT INTO TRAINING AND VALIDATION
    script = f"""
    %run ramp-code/scripts/make_train_val_split_lists.py -src {dst_path}/chips -pfx {uid}_fair_split -trn 0.85 -val 0.15
    """

    # Use the exec function to execute the script as a string
    exec(script)

    # move all the VALIDATION chips, labels and masks to their new locations
    mv_script = f"""
    %run ramp-code/scripts/move_chips_from_csv.py -sd {dst_path}/chips -td {dst_path}/val-chips -csv {uid}_fair_split_val.csv -mv

    %run ramp-code/scripts/move_chips_from_csv.py -sd {dst_path}/labels -td {dst_path}/val-labels -csv {uid}_fair_split_val.csv -mv

    %run ramp-code/scripts/move_chips_from_csv.py -sd {dst_path}/binarymasks -td {dst_path}/val-binarymasks -csv {uid}_fair_split_val.csv -mv
    """
    exec(mv_script)
    return uid
