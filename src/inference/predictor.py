"""High-level prediction interface for DR classification with explanations.

This module provides a simple interface to run inference and generate
Grad-CAM++ explainability visualizations for single images.
"""

import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from typing import Union, Dict, Optional
from PIL import Image
import cv2

from src.inference.model_loader import load_resnet50_dr_model
from src.inference.explainability import (
    setup_gradcam,
    generate_gradcam,
)
from src.config import CLASS_NAMES, DEVICE
from src.utils.image_io import save_pil_image


# Global model and explainability objects (lazy loaded)
_model = None
_cam = None


def _get_model():
    """Lazy load model singleton."""
    global _model
    if _model is None:
        _model = load_resnet50_dr_model()
    return _model


def _get_gradcam():
    """Lazy load Grad-CAM++ singleton."""
    global _cam
    if _cam is None:
        model = _get_model()
        _cam = setup_gradcam(model)
    return _cam


def predict_with_explanations(
    image_input: Union[str, Path, Image.Image],
    save_dir: Optional[Union[str, Path]] = None
) -> Dict:
    """Run prediction with Grad-CAM++ explainability visualization.
    
    Args:
        image_input: Image file path (str/Path) or PIL.Image object
        save_dir: Optional directory to save Grad-CAM++ overlay.
                 If None, overlay is not saved.
    
    Returns:
        Dictionary with:
        - pred_class_idx: Predicted class index (int)
        - pred_class_name: Predicted class name (str)
        - confidence: Confidence score (float)
        - probs: List of probabilities for all 5 classes (list of floats)
        - gradcam_overlay_path: Path to saved Grad-CAM++ overlay (str or None)
    """
    # Load and preprocess image
    if isinstance(image_input, (str, Path)):
        original_img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):
        original_img = image_input.convert("RGB")
    else:
        raise TypeError(
            f"image_input must be str, Path, or PIL.Image, got {type(image_input)}"
        )
    
    # Keep original image dimensions for overlay
    original_size = original_img.size  # (width, height)
    
    # Apply transforms for model input (Resize, CenterCrop, ToTensor, Normalize)
    # Note: SmartFundusCrop removed for simpler visualization
    from torchvision import transforms
    from src.config import IMG_SIZE, IMG_RESIZE, IMAGENET_MEAN, IMAGENET_STD
    
    # First resize to IMG_RESIZE to match preprocessing
    resized_img = transforms.Resize(IMG_RESIZE)(original_img)
    
    # Then apply center crop and normalization for model
    model_transforms = transforms.Compose([
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    img_tensor = model_transforms(resized_img)
    img_tensor = img_tensor.unsqueeze(0).to(DEVICE)  # Add batch dimension
    
    # Get model and run prediction
    model = _get_model()
    
    with torch.no_grad():
        logits = model(img_tensor)
        probs = F.softmax(logits, dim=1)[0].cpu().numpy()
    
    pred_class_idx = int(probs.argmax())
    pred_class_name = CLASS_NAMES[pred_class_idx]
    confidence = float(probs[pred_class_idx])
    
    # Generate Grad-CAM++ visualization
    gradcam_overlay_path = None
    
    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Grad-CAM heatmap on processed image (224x224)
        cam = _get_gradcam()
        grayscale_cam, overlay_224, _ = generate_gradcam(
            model, cam, img_tensor, target_class=pred_class_idx
        )
        
        # Resize heatmap to match the original image size
        heatmap_uint8 = (grayscale_cam * 255).astype(np.uint8)
        heatmap_resized = cv2.resize(
            heatmap_uint8,
            original_size,  # (width, height) - resize to original image
            interpolation=cv2.INTER_LINEAR
        )
        # Normalize back to [0, 1]
        heatmap_normalized = heatmap_resized.astype(np.float32) / 255.0
        
        # Convert original image to numpy array
        original_np = np.array(original_img).astype(np.uint8)
        if len(original_np.shape) == 2:
            original_np = cv2.cvtColor(original_np, cv2.COLOR_GRAY2RGB)
        
        # Create heatmap using JET colormap
        heatmap = cv2.applyColorMap(np.uint8(255 * heatmap_normalized), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Create overlay on the original image (0.6 original, 0.4 heatmap)
        overlay = cv2.addWeighted(original_np, 0.6, heatmap, 0.4, 0)
        
        # Convert to PIL and save
        gradcam_img = Image.fromarray(overlay, mode='RGB')
        gradcam_path = save_dir / "gradcam_overlay.png"
        save_pil_image(gradcam_img, gradcam_path)
        gradcam_overlay_path = str(gradcam_path)
    
    return {
        "pred_class_idx": pred_class_idx,
        "pred_class_name": pred_class_name,
        "confidence": confidence,
        "probs": [float(p) for p in probs],
        "gradcam_overlay_path": gradcam_overlay_path,
    }
