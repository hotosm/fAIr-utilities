from typing import List

import numpy as np
import torch
from PIL import Image
from tensorflow import keras
from ultralytics import YOLO, FastSAM

IMAGE_SIZE = 256


def open_images(paths: List[str]) -> np.ndarray:
    """Open images from some given paths."""
    images = []
    for path in paths:
        image = keras.preprocessing.image.load_img(
            path, target_size=(IMAGE_SIZE, IMAGE_SIZE)
        )
        image = np.array(image.getdata()).reshape(IMAGE_SIZE, IMAGE_SIZE, 3) / 255.0
        images.append(image)

    return np.array(images)


def save_mask(mask: np.ndarray, filename: str) -> None:
    """Save the mask array to the specified location."""
    reshaped_mask = mask.reshape((IMAGE_SIZE, IMAGE_SIZE)) * 255
    result = Image.fromarray(reshaped_mask.astype(np.uint8))
    result.save(filename)


def initialize_model(path, device=None):
    """Loads either keras or pytorch model."""
    if not device:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if path.lower() == "yolo":  # Ultralytics pretrained YOLOv8
        model = YOLO('yolov8n-seg.pt')
    elif path.lower() == "fastsam":  # Ultralytics pretrained FastSAM
        model = FastSAM('FastSAM-s.pt')
    elif path.endswith('.pth') or path.endswith('.pt'):  # Pytorch saved checkpoint
        model = torch.load(path, map_location=device)
    elif path.endswith('.pb') or path.endswith('.tf'):  # Tensorflow saved checkpoint
        model = keras.models.load_model(path)
    else:
        raise ValueError("Unsupported model format or path")

    return model
