# Standard library imports
import os
import time
import warnings
import ultralytics

os.environ.update(os.environ)
os.environ["RAMP_HOME"] = os.getcwd()


# Reader import
from hot_fair_utilities import polygonize, predict, preprocess
from hot_fair_utilities.preprocessing.yolo_v8_v2.yolo_format import yolo_format
from hot_fair_utilities.training.yolo_v8_v2.train import train as train_yolo

warnings.simplefilter(action="ignore", category=FutureWarning)


class print_time:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        print(f"{self.name} took {round(time.perf_counter() - self.start, 2)} seconds")


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
        multimasks=False,
        epsg=4326
    )

yolo_data_dir = f"{base_path}/yolo_v2"
with print_time("yolo conversion"):
    yolo_format(
        input_path=preprocess_output,
        output_path=yolo_data_dir,
    )

output_model_path,output_model_iou_accuracy = train_yolo(
    data=f"{base_path}",
    weights=f"{os.getcwd()}/yolov8s_v2-seg.pt", 
    # gpu="cpu",
    epochs=2,
    batch_size=16,
    pc=2.0,
    output_path=yolo_data_dir,
    dataset_yaml_path=os.path.join(yolo_data_dir,'yolo_dataset.yaml')
)
print(output_model_iou_accuracy)

prediction_output = f"{base_path}/prediction/output"
# model_path = f"{output_path}/weights/best.pt"
with print_time("inference"):
    predict(
        checkpoint_path=output_model_path,
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
