import logging
import os
import shutil

from tensorflow import keras

log = logging.getLogger(__name__)


def _export_saved_model_to_h5(saved_model_path: str) -> str:
    h5_path = f"{saved_model_path}.h5"
    model = keras.models.load_model(saved_model_path)
    model.save(h5_path)
    keras.backend.clear_session()
    log.info("Exported checkpoint to %s", h5_path)
    return h5_path


def extract_highest_accuracy_model(output_path):
    model_checkpoints = os.path.join(output_path, "model-checkpts")
    assert os.path.exists(model_checkpoints), "Model Checkpoints Doesn't Exist"
    entries = os.listdir(model_checkpoints)
    assert len(entries) > 0, "Couldn't find any models"
    # Create a variable to store the latest entry
    latest_entry = None

    # Create a variable to store the latest entry's modification time
    latest_time = 0

    # Iterate over the list of entries
    for entry in entries:
        # Use the os.stat() method to get the entry's modification time
        entry_time = os.stat(os.path.join(model_checkpoints, entry)).st_mtime
        # Check if the entry's modification time is greater than the latest time
        if entry_time > latest_time:
            # If the entry's modification time is greater, update the latest time and entry variables
            latest_time = entry_time
            latest_entry = entry

    # get the highest accuracy model one
    latest_entry_path = os.path.join(model_checkpoints, latest_entry)  # ty: ignore[no-matching-overload]
    log.info("Latest checkpoint: %s", latest_entry_path)
    highest_accuracy = 0
    highest_accuracy_entry = None
    for entry in os.listdir(latest_entry_path):
        parts = entry.split("_")

        accuracy = parts[-1][:-3]  # remove .tf
        if float(accuracy) * 100 > highest_accuracy:
            highest_accuracy_entry = entry
            highest_accuracy = float(accuracy) * 100
    log.info("Highest accuracy model: %s (%.2f%%)", highest_accuracy_entry, highest_accuracy)
    for entry in os.listdir(latest_entry_path):
        # Check if the entry is not the file or directory you want to keep
        if entry != highest_accuracy_entry:
            # If the entry is not the file or directory you want to keep, use the os.remove() method to remove it
            shutil.rmtree(os.path.join(latest_entry_path, entry))
    best_saved_model_path = os.path.join(  # ty: ignore[no-matching-overload]
        latest_entry_path, highest_accuracy_entry
    )
    best_h5_path = _export_saved_model_to_h5(best_saved_model_path)
    return highest_accuracy, best_h5_path
