from pathlib import Path
from PIL import Image
import torch

from src.data.transforms import validation_transform

def load_and_preprocess(image_path: Path) -> torch.Tensor:
    img = Image.open(image_path).convert("RGB")
    t = validation_transform(img)
    return t.unsqueeze(0)  # [1, C, H, W]
