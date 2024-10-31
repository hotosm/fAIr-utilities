# Standard library imports
import os
import time
from glob import glob
from pathlib import Path

# Third party imports
import numpy as np
import torch
from tensorflow import keras
from ultralytics import YOLO

from ..georeferencing import georeference
from ..utils import remove_files
from .utils import initialize_model, open_images, save_mask

BATCH_SIZE = 8
IMAGE_SIZE = 256
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


def predict(
    checkpoint_path: str,
    input_path: str,
    prediction_path: str,
    confidence: float = 0.5,
    remove_images=True,
) -> None:
    """Predict building footprints for aerial images given a model checkpoint.

    This function reads the model weights from the checkpoint path and outputs
    predictions in GeoTIF format. The input images have to be in PNG format.

    The predicted masks will be georeferenced with EPSG:3857 as CRS.

    Args:
        checkpoint_path: Path where the weights of the model can be found.
        input_path: Path of the directory where the images are stored.
        prediction_path: Path of the directory where the predicted images will go.
        confidence: Threshold probability for filtering out low-confidence predictions.
        remove_images: Bool indicating whether delete prediction images after they were georeferenced.

    Example::

        predict(
            "model_1_checkpt.tf",
            "data/inputs_v2/4",
            "data/predictions/4"
        )
    """
    start = time.time()
    print(f"Using : {checkpoint_path}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = initialize_model(checkpoint_path, device=device)
    print(f"It took {round(time.time()-start)} sec to load model")
    start = time.time()

    os.makedirs(prediction_path, exist_ok=True)
    image_paths = glob(f"{input_path}/*.png") + glob(f"{input_path}/*.tif")

    if isinstance(model, keras.Model):
        for i in range((len(image_paths) + BATCH_SIZE - 1) // BATCH_SIZE):
            image_batch = image_paths[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
            images = open_images(image_batch)
            images = images.reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 3)

            preds = model.predict(images)
            preds = np.argmax(preds, axis=-1)
            preds = np.expand_dims(preds, axis=-1)
            preds = np.where(
                preds > confidence, 1, 0
            )  # Filter out low confidence predictions

            for idx, path in enumerate(image_batch):
                save_mask(
                    preds[idx],
                    str(f"{prediction_path}/{Path(path).stem}.png"),
                )
    elif isinstance(model, YOLO):
        for idx in range(0, len(image_paths), BATCH_SIZE):
            batch = image_paths[idx : idx + BATCH_SIZE]
            for i, r in enumerate(
                model.predict(batch, conf=confidence, imgsz=IMAGE_SIZE, verbose=False)
            ):
                if hasattr(r, "masks") and r.masks is not None:
                    preds = (
                        r.masks.data.max(dim=0)[0].detach().cpu().numpy()
                    )  # Combine masks and convert to numpy

                else:
                    preds = np.zeros(
                        (
                            IMAGE_SIZE,
                            IMAGE_SIZE,
                        ),
                        dtype=np.float32,
                    )  # Default if no masks

                save_mask(preds, str(f"{prediction_path}/{Path(batch[i]).stem}.png"))
    else:
        raise RuntimeError("Loaded model is not supported")

    print(
        f"It took {round(time.time()-start)} sec to predict with {confidence} Confidence Threshold"
    )
    if isinstance(model, keras.Model):
        keras.backend.clear_session()
    del model
    start = time.time()

    georeference(prediction_path, prediction_path, is_mask=True)
    print(f"It took {round(time.time()-start)} sec to georeference")

    if remove_images:
        remove_files(f"{prediction_path}/*.xml")
        remove_files(f"{prediction_path}/*.png")
