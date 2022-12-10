# Standard library imports
import os
from .prepare_data split_training_2_validation
from .run_training import manage_fine_tuning_config,run_main_train_code

def train(
    input_path: str,
    epoch_size: int,
    batch_size: int,
    model: str,
    model_home: str,
) -> None:
    """Trains the input image with base model

    The preprocessed images and labels are in the EPSG:3857 projected
    coordinate system ('WGS 84 / Pseudo-Mercator', coordinates
    in meters).

    Args:
        input_path: Path of the directory output by preprocess
        epoch_size: Epoch size to be used for training
        batch_size: Batch size to be used for training
        model : Choose Model, Options supported are , ramp
        model_home : Model Home directory which contains necessary file in order to run model
    Example::

        train(
            "data/region1_preprocessed",
            2,
            2,
            ramp,
            ../ramp-home
        )
    """
    assert os.path.exists(input_path), "Input Path Doesn't Exist"
    assert os.path.exists(model_home), "Model Home Doesn't Exist"
    supported_models = ["ramp"]

    # Use the assert keyword to raise an AssertionError if the input model string is not in the list of supported models
    assert any(
        model.lower() in supported_model for supported_model in supported_models
    ), "Model is not in the list of supported models"

    # Export the environment variables from the operating system
    os.environ.update(os.environ)
    if model.lower() == 'ramp': 
        # Add a new environment variable to the operating system
        os.environ["RAMP_HOME"] = model_home
        # Print the environment variables to verify that the new variable was added
        print(os.environ)
        uid=split_training_2_validation(input_path)
        cfg=manage_fine_tuning_config(uid,epoch_size,batch_size)
        run_main_train_code(cfg)

