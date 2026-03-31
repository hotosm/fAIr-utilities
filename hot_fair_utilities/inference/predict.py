import os
from glob import glob

from .._logging import get_logger
from ..utils import remove_files

log = get_logger(__name__)


def predict(
    checkpoint_path: str,
    input_path: str,
    prediction_path: str,
    confidence: float = 0.5,
    remove_images: bool = True,
) -> None:
    """Predict building footprints for aerial images given a model checkpoint.

    Delegates to fairpredictor's run_prediction for model loading, batch
    inference, and mask generation. Then georeferences the output masks.

    The predicted masks will be georeferenced with EPSG:3857 as CRS.

    Args:
        checkpoint_path: Path where the weights of the model can be found.
        input_path: Directory containing PNG or TIF input images.
        prediction_path: Directory for the predicted output.
        confidence: Threshold probability for filtering low-confidence predictions.
        remove_images: Delete intermediate PNG/XML files after georeferencing.
    """
    from predictor.prediction import run_prediction

    os.makedirs(prediction_path, exist_ok=True)

    has_tif = bool(glob(f"{input_path}/*.tif"))
    has_png = bool(glob(f"{input_path}/*.png"))

    if not (has_tif or has_png):
        raise FileNotFoundError(f"No .tif or .png images found in {input_path}")

    georef_path = run_prediction(checkpoint_path, input_path, prediction_path, confidence, crs="3857")

    tif_files = glob(f"{georef_path}/*.tif")
    for tif_file in tif_files:
        dest = os.path.join(prediction_path, os.path.basename(tif_file))
        if tif_file != dest:
            os.replace(tif_file, dest)

    if remove_images:
        remove_files(f"{prediction_path}/*.xml")
        remove_files(f"{prediction_path}/*.png")

    log.info("Prediction complete: %d georeferenced masks in %s", len(tif_files), prediction_path)
