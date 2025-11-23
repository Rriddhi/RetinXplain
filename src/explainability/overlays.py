import numpy as np
import cv2
from PIL import Image

def overlay_heatmap_on_image(image: Image.Image, heatmap: np.ndarray, alpha: float = 0.4):
    """
    image: PIL RGB image
    heatmap: H x W normalized [0,1]
    """
    image = image.resize((heatmap.shape[1], heatmap.shape[0]))
    img_np = np.array(image)

    heatmap_color = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    overlay = (alpha * heatmap_color + (1 - alpha) * img_np).astype(np.uint8)
    return Image.fromarray(overlay)
