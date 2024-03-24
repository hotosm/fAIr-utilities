import os
import time
import warnings
import tensorflow as tf

from hot_fair_utilities import preprocess, predict, polygonize
from hot_fair_utilities.preprocessing.yolo_format import yolo_format
from train_yolo import train as train_yolo

warnings.simplefilter(action='ignore', category=FutureWarning)


class print_time:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        print(f"{self.name} took {round(time.perf_counter() - self.start, 2)} seconds")


print(
    f"\nUsing tensorflow version {tf.__version__} with no of gpu : {len(tf.config.experimental.list_physical_devices('GPU'))}\n"
)
os.environ.update(os.environ)
os.environ["RAMP_HOME"] = os.getcwd()
print(os.environ["RAMP_HOME"])

start_time = time.time()
base_path = f"{os.getcwd()}/ramp-data/sample_2"

model_input_image_path = f"{base_path}/input"
preprocess_output = f"{base_path}/preprocessed"
with print_time("preprocessing"):
    preprocess(
        input_path=model_input_image_path,
        output_path=preprocess_output,
        rasterize=True,
        rasterize_options=["binary"],
        georeference_images=True,
        multimasks=True  # new arg
    )

yolo_data_dir = f"{base_path}/yolo"
with print_time("yolo conversion"):
    yolo_format(
        preprocessed_dirs=preprocess_output,
        yolo_dir=yolo_data_dir,
        multimask=True,
        p_val=0.05
    )

train_yolo(data=f"{base_path}",
               weights=f"{os.getcwd()}/checkpoints/yolov8n-seg_ramp-training_ep500_bs16_deg30_pc2.0/weights/best.pt",
               gpu="cpu",
               epochs=2,
               batch_size=16,
               pc=2.0
               )

prediction_output = f"{base_path}/prediction/output"
model_path = f"{os.getcwd()}/checkpoints/yolov8n-seg_sample_2_ep2_bs16_pc2.0/weights/best.pt"
with print_time("inference"):
    predict(
        checkpoint_path=model_path,
        input_path=f"{base_path}/prediction/input",
        prediction_path=prediction_output,
    )

geojson_output = f"{prediction_output}/prediction.geojson"
with print_time("polygonization"):
    polygonize(
        input_path=prediction_output,
        output_path=geojson_output,
        remove_inputs=False,
    )

print(f"\n Total Process Completed in : {time.time()-start_time} sec")
