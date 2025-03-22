# %%
# Standard library imports
import os
import time

# Third party imports
import tensorflow as tf

print(
    f"\nUsing tensorflow version {tf. __version__} with no of gpu : {len(tf.config.experimental.list_physical_devices('GPU'))}\n"
)
# print(os.getcwd())
# os.environ.update(os.environ)

# Add a new environment variable to the operating system
# os.environ["RAMP_HOME"] = os.getcwd()
# Print the environment variables to verify that the new variable was added
# print(os.environ["RAMP_HOME"])

start_time = time.time()
# Third party imports
# %%
# import ramp.utils

# Reader imports
# import hot_fair_utilities
top_level_repo_folder_path = str(os.system("git rev-parse --show-toplevel"))
sample_ramp_data_folder_path = os.path.join(top_level_repo_folder_path,'ramp-data/sample_2')

# Reader imports
# %%
from hot_fair_utilities import preprocess

ramp_sample_input_folder = os.path.join(sample_ramp_data_folder_path,'input')
# model_input_image_path = f"{base_path}/input"
ramp_sample_preprocessed_folder = os.path.join(sample_ramp_data_folder_path,'preprocessed')
# preprocess_output = f"/{base_path}/preprocessed"
preprocess(
    input_path=ramp_sample_input_folder,
    output_path=ramp_sample_preprocessed_folder,
    rasterize=True,
    rasterize_options=["binary"],
    georeference_images=True,
    # multimasks=True,
    multimasks=False
)

# Reader imports
# %%
from hot_fair_utilities.training.ramp import train

# %%
# train_output = f"{base_path}/train"
ramp_sample_ready_for_training_folder = os.path.join(sample_ramp_data_folder_path,'ready_for_trainining')
final_accuracy, final_model_path = train(
    input_path=ramp_sample_preprocessed_folder,
    output_path=ramp_sample_ready_for_training_folder,
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

# prediction_output = f"{base_path}/prediction/output"
prediction_input = os.path.join(sample_ramp_data_folder_path,'prediction/input')
prediiction_output = os.path.join(sample_ramp_data_folder_path,'prediction/output')

predict(
    checkpoint_path=final_model_path,
    input_path=prediction_input,
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

print(f"\n Total Process Completed in : {time.time()-start_time} sec")
