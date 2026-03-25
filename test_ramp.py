# %%
# Standard library imports
import os
import sys
import time
import types

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Third party imports
import tensorflow as tf

from hot_fair_utilities import polygonize, predict, preprocess
from hot_fair_utilities.training.ramp import train

experimental_layers_module = types.ModuleType("tensorflow.keras.layers.experimental")
setattr(experimental_layers_module, "preprocessing", getattr(tf, "keras").layers)
sys.modules["tensorflow.keras.layers.experimental"] = experimental_layers_module

gpu_count = len(tf.config.experimental.list_physical_devices("GPU"))
print(f"\nUsing tensorflow version {tf.__version__} with no of gpu : {gpu_count}\n")
print(os.getcwd())
os.environ.update(os.environ)
# Add a new environment variable to the operating system
os.environ["RAMP_HOME"] = os.getcwd()
# Print the environment variables to verify that the new variable was added
print(os.environ["RAMP_HOME"])

start_time = time.time()
# Third party imports
# %%
# import ramp.utils

base_path = f"{os.getcwd()}/ramp-data/sample_2"

model_input_image_path = f"{base_path}/input"
preprocess_output = f"{base_path}/preprocessed"
preprocess(
    input_path=model_input_image_path,
    output_path=preprocess_output,
    rasterize=True,
    rasterize_options=["binary"],
    georeference_images=True,
    multimasks=True,
)

train_output = f"{base_path}/train"
final_accuracy, final_model_path = train(
    input_path=preprocess_output,
    output_path=train_output,
    epoch_size=2,
    batch_size=2,
    model="ramp",
    model_home=os.environ["RAMP_HOME"],
)

# %%
print(final_accuracy, final_model_path)

prediction_output = f"{base_path}/prediction/output"
predict(
    checkpoint_path=final_model_path,
    input_path=f"{base_path}/prediction/input",
    prediction_path=prediction_output,
)

geojson_output = f"{prediction_output}/prediction.geojson"
polygonize(
    input_path=prediction_output,
    output_path=geojson_output,
    remove_inputs=True,
)

print(f"\n Total Process Completed in : {time.time() - start_time} sec")
