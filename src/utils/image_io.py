from pathlib import Path
from PIL import Image

def save_pil_image(img: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")
