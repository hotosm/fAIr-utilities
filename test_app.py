# %%
# Standard library imports
import os

# Third party imports
import tensorflow as tf

print(
    f"\nUsing tensorflow version {tf. __version__} with no of gpu : {len(tf.config.experimental.list_physical_devices('GPU'))}\n"
)
print(os.getcwd())
os.environ.update(os.environ)
# Add a new environment variable to the operating system
os.environ["RAMP_HOME"] = os.getcwd()
# Print the environment variables to verify that the new variable was added
print(os.environ["RAMP_HOME"])

# Third party imports
# %%
import ramp.utils

# Reader imports
import hot_fair_utilities

base_path = f"{os.getcwd()}/ramp-data/sample_2"

# Reader imports
# %%
from hot_fair_utilities import preprocess

model_input_image_path = f"{base_path}/input"
preprocess_output = f"/{base_path}/preprocessed"
preprocess(
    input_path=model_input_image_path,
    output_path=preprocess_output,
    rasterize=True,
    rasterize_options=["binary"],
    georeference_images=True,
)

# Reader imports
# %%
from hot_fair_utilities import train

# %%
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

# Reader imports
# %%
from hot_fair_utilities import predict

prediction_output = f"{base_path}/prediction/output"
predict(
    checkpoint_path=final_model_path,
    input_path=f"{base_path}/prediction/input",
    prediction_path=prediction_output,
)

# Reader imports
# %%
from hot_fair_utilities import polygonize

geojson_output = f"{prediction_output}/prediction.geojson"
polygonize(
    input_path=prediction_output,
    output_path=geojson_output,
    remove_inputs=True,
)
