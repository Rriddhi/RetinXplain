import numpy as np
import cv2
from PIL import Image
import torch
from torchvision import transforms
from src.config import IMG_SIZE, IMG_RESIZE, IMAGENET_MEAN, IMAGENET_STD


class SmartFundusCrop:
    def __call__(self, img: Image.Image) -> Image.Image:
        np_img = np.array(img)
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)

        _, thresh = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY)
        coords = cv2.findNonZero(thresh)
        if coords is None:
            return img

        x, y, w, h = cv2.boundingRect(coords)
        cropped = np_img[y:y + h, x:x + w]

        h2, w2 = cropped.shape[:2]
        side = int(min(w2, h2) * 0.95)
        cx, cy = w2 // 2, h2 // 2
        x0, y0 = cx - side // 2, cy - side // 2
        square = cropped[y0:y0 + side, x0:x0 + side]

        return Image.fromarray(square)


validation_transform = transforms.Compose([
    SmartFundusCrop(),
    transforms.Resize(IMG_RESIZE),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])


def denorm(img_tensor: torch.Tensor) -> torch.Tensor:
    if img_tensor.ndim == 3:
        mean = torch.tensor(IMAGENET_MEAN, device=img_tensor.device).view(3, 1, 1)
        std  = torch.tensor(IMAGENET_STD,  device=img_tensor.device).view(3, 1, 1)
    else:
        raise ValueError(f"Expected 3D tensor, got {img_tensor.shape}")
    return img_tensor * std + mean
