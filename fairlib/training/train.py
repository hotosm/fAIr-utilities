# Standard library imports
import os

from .cleanup import extract_highest_accuracy_model
from .prepare_data import split_training_2_validation
from .run_training import manage_fine_tuning_config, run_main_train_code


def train(
    input_path: str,
    output_path: str,
    epoch_size: int,
    batch_size: int,
    model: str,
    model_home: str,
):
    """Trains the input image with base model


    Args:
        input_path: Path of the directory output by preprocess
        output_path: Path of the working dir for training
        epoch_size: Epoch size to be used for training
        batch_size: Batch size to be used for training
        model : Choose Model, Options supported are , ramp
        model_home : Model Home directory which contains necessary file in order to run model
    Example::

        final_accuracy, final_model_path = train(
            input_path=preprocess_output,
            epoch_size=2,
            batch_size=2,
            model="ramp",
            model_home=os.environ["RAMP_HOME"],
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
    if model.lower() == "ramp":
        # Add a new environment variable to the operating system
        os.environ["RAMP_HOME"] = model_home
        # Print the environment variables to verify that the new variable was added
        print("Starting to prepare data for training")
        split_training_2_validation(input_path, output_path)
        cfg = manage_fine_tuning_config(output_path, epoch_size, batch_size)
        print("Data is ready for training")
        run_main_train_code(cfg)
        print("extracting highest accuracy model")
        final_accuracy, final_model_path = extract_highest_accuracy_model(output_path)
        return (final_accuracy, final_model_path)
