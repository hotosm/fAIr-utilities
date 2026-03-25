# Standard library imports
import os
import time
import warnings

# Reader imports
from hot_fair_utilities import polygonize, predict, preprocess
from hot_fair_utilities.preprocessing.yolo_v8.yolo_format import yolo_format
from hot_fair_utilities.training.yolo_v8.train import train as train_yolo

warnings.simplefilter(action="ignore", category=FutureWarning)


def main() -> None:
    start_time = time.perf_counter()
    workspace = os.getcwd()

    base_path = f"{workspace}/ramp-data/sample_2"
    preprocess_output = f"{base_path}/preprocessed"
    preprocess_start = time.perf_counter()
    preprocess(
        input_path=f"{base_path}/input",
        output_path=preprocess_output,
        rasterize=True,
        rasterize_options=["binary"],
        georeference_images=True,
        multimasks=False,
        epsg=4326,
    )
    print(f"preprocessing took {round(time.perf_counter() - preprocess_start, 2)} seconds")

    yolo_data_dir = f"{base_path}/yolo_v2"
    conversion_start = time.perf_counter()
    yolo_format(
        input_path=preprocess_output,
        output_path=yolo_data_dir,
    )
    print(f"yolo conversion took {round(time.perf_counter() - conversion_start, 2)} seconds")

    output_model_path, output_model_iou_accuracy = train_yolo(
        data=base_path,
        weights=f"{workspace}/yolov8s_v2-seg.pt",
        epochs=2,
        batch_size=16,
        pc=2.0,
        output_path=yolo_data_dir,
        dataset_yaml_path=os.path.join(yolo_data_dir, "yolo_dataset.yaml"),
    )
    print(output_model_iou_accuracy)

    prediction_output = f"{base_path}/prediction/output"
    inference_start = time.perf_counter()
    predict(
        checkpoint_path=output_model_path,
        input_path=f"{base_path}/prediction/input",
        prediction_path=prediction_output,
    )
    print(f"inference took {round(time.perf_counter() - inference_start, 2)} seconds")

    polygonize_start = time.perf_counter()
    polygonize(
        input_path=prediction_output,
        output_path=f"{prediction_output}/prediction.geojson",
        remove_inputs=False,
    )
    print(f"polygonization took {round(time.perf_counter() - polygonize_start, 2)} seconds")

    print(f"\n Total Process Completed in : {time.perf_counter() - start_time} sec")


if __name__ == "__main__":
    main()
