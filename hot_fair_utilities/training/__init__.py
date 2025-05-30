"""
Training module for fAIr-utilities.

This module provides training functionality for different model types:
- RAMP training for building detection
- YOLO v8 training for object detection and segmentation
"""

from .ramp import train as ramp_train
from .yolo_v8_v1 import train as yolo_v8_v1_train
from .yolo_v8_v2 import train as yolo_v8_v2_train

__all__ = [
    "ramp_train",
    "yolo_v8_v1_train",
    "yolo_v8_v2_train"
]