from typing import List

import numpy as np
from PIL import Image
from tensorflow import keras

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
