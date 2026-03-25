import os
import time

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Third party imports
import tensorflow as tf

from hot_fair_utilities import patch_tf_experimental_layers, polygonize, predict, preprocess
from hot_fair_utilities.training.ramp import train

patch_tf_experimental_layers()


def main() -> None:
    start_time = time.perf_counter()
    workspace = os.getcwd()
    os.environ["RAMP_HOME"] = workspace

    gpu_count = len(tf.config.experimental.list_physical_devices("GPU"))
    print(f"\nUsing tensorflow version {tf.__version__} with no of gpu : {gpu_count}\n")

    base_path = f"{workspace}/ramp-data/sample_2"
    preprocess_output = f"{base_path}/preprocessed"
    preprocess(
        input_path=f"{base_path}/input",
        output_path=preprocess_output,
        rasterize=True,
        rasterize_options=["binary"],
        georeference_images=True,
        multimasks=True,
    )

    final_accuracy, final_model_path = train(
        input_path=preprocess_output,
        output_path=f"{base_path}/train",
        epoch_size=1,
        batch_size=2,
        model="ramp",
        model_home=os.environ["RAMP_HOME"],
    )
    print(final_accuracy, final_model_path)

    prediction_output = f"{base_path}/prediction/output"
    predict(
        checkpoint_path=final_model_path,
        input_path=f"{base_path}/prediction/input",
        prediction_path=prediction_output,
    )
    polygonize(
        input_path=prediction_output,
        output_path=f"{prediction_output}/prediction.geojson",
        remove_inputs=True,
    )

    print(f"\n Total Process Completed in : {time.perf_counter() - start_time} sec")


if __name__ == "__main__":
    main()
