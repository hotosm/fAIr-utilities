from typing import List

import numpy as np
import torch
from PIL import Image
from tensorflow import keras
from ultralytics import YOLO


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
    """Loads either keras or yolo model."""
    if not isinstance(path, str):  # probably loaded model
        return path

    if path.endswith('.pt'):  # YOLO
        if not device:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = YOLO(path).to(device)
    else:
        model = keras.models.load_model(path)
    return model
