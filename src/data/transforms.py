"""Image transforms and SmartFundusCrop placeholder."""
from PIL import Image

def get_val_transforms():
    # Return a callable that converts a PIL image -> resized image
    def _transform(img: Image.Image):
        return img.resize((512, 512))
    return _transform

def get_aptos_transforms():
    return get_val_transforms()
