import os
from glob import glob
from pathlib import Path

import numpy as np
from tensorflow import keras

from ..georeferencing import georeference
from ..utils import remove_files
from .utils import open_images, save_mask

BATCH_SIZE = 8
IMAGE_SIZE = 256
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


def predict(checkpoint_path: str, input_path: str, prediction_path: str) -> None:
    """Predict building footprints for aerial images given a model checkpoint.

    This function reads the model weights from the checkpoint path and outputs
    predictions in GeoTIF format. The input images have to be in PNG format.

    The predicted masks will be georeferenced with EPSG:3857 as CRS.

    Args:
        checkpoint_path: Path where the weights of the model can be found.
        input_path: Path of the directory where the images are stored.
        prediction_path: Path of the directory where the predicted images will go.

    Example::

        predict(
            "model_1_checkpt.tf",
            "data/inputs_v2/4",
            "data/predictions/4"
        )
    """
    model = keras.models.load_model(checkpoint_path)

    os.makedirs(prediction_path, exist_ok=True)
    image_paths = glob(f"{input_path}/*.png")

    for i in range((len(image_paths) + BATCH_SIZE - 1) // BATCH_SIZE):
        image_batch = image_paths[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
        images = open_images(image_batch)
        images = images.reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 3)

        preds = model.predict(images)
        preds = np.argmax(preds, axis=-1)
        preds = np.expand_dims(preds, axis=-1)
        preds = np.where(preds > 0.5, 1, 0)

        for idx, path in enumerate(image_batch):
            save_mask(
                preds[idx],
                str(f"{prediction_path}/{Path(path).stem}.png"),
            )

    georeference(prediction_path, prediction_path, is_mask=True)
    remove_files(f"{prediction_path}/*.xml")
    remove_files(f"{prediction_path}/*.png")
