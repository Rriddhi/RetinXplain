"""Helpers for loading a PIL image and converting to model-ready tensor.

This is a small stub; replace with torchvision transforms / normalization used by your model.
"""
from PIL import Image
import numpy as np

def load_image_to_array(path: str):
    img = Image.open(path).convert("RGB")
    return np.array(img)
