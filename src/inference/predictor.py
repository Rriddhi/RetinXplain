"""High-level prediction interface for DR classification with explanations.

This module provides a simple interface to run inference and generate
explainability visualizations for single images.
"""

import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from typing import Union, Dict, Optional
from PIL import Image

from src.inference.model_loader import load_resnet50_dr_model
from src.inference.explainability import (
    setup_gradcam,
    generate_gradcam,
    setup_lime,
    generate_lime,
    setup_shap,
    generate_shap
)
from src.data.transforms import validation_transform
from src.config import CLASS_NAMES, DEVICE, IMAGENET_MEAN, IMAGENET_STD
from src.utils.image_io import save_pil_image


# Global model and explainability objects (lazy loaded)
_model = None
_cam = None
_lime_explainer = None
_lime_predict_fn = None
_shap_explainer = None
_shap_background = None


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


def _get_lime():
    """Lazy load LIME explainer singleton."""
    global _lime_explainer, _lime_predict_fn
    if _lime_explainer is None:
        model = _get_model()
        _lime_explainer, _lime_predict_fn = setup_lime(model)
    return _lime_explainer, _lime_predict_fn


def _get_shap():
    """Lazy load SHAP explainer singleton."""
    global _shap_explainer, _shap_background
    if _shap_explainer is None:
        model = _get_model()
        _shap_explainer, _shap_background = setup_shap(model)
    return _shap_explainer


def predict_with_explanations(
    image_input: Union[str, Path, Image.Image],
    save_dir: Optional[Union[str, Path]] = None
) -> Dict:
    """Run prediction with explainability visualizations.
    
    Args:
        image_input: Image file path (str/Path) or PIL.Image object
        save_dir: Optional directory to save Grad-CAM++ and LIME overlays.
                 If None, overlays are not saved.
    
    Returns:
        Dictionary with:
        - pred_class_idx: Predicted class index (int)
        - pred_class_name: Predicted class name (str)
        - confidence: Confidence score (float)
        - probs: List of probabilities for all 5 classes (list of floats)
        - gradcam_overlay_path: Path to saved Grad-CAM++ overlay (str or None)
        - lime_overlay_path: Path to saved LIME overlay (str or None)
        - shap_overlay_path: Path to saved SHAP overlay (str or None)
    """
    # Load and preprocess image
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise TypeError(
            f"image_input must be str, Path, or PIL.Image, got {type(image_input)}"
        )
    
    # Apply validation transforms
    img_tensor = validation_transform(img)
    img_tensor = img_tensor.unsqueeze(0).to(DEVICE)  # Add batch dimension
    
    # Get model and run prediction
    model = _get_model()
    
    with torch.no_grad():
        logits = model(img_tensor)
        probs = F.softmax(logits, dim=1)[0].cpu().numpy()
    
    pred_class_idx = int(probs.argmax())
    pred_class_name = CLASS_NAMES[pred_class_idx]
    confidence = float(probs[pred_class_idx])
    
    # Generate explainability visualizations
    gradcam_overlay_path = None
    lime_overlay_path = None
    shap_overlay_path = None
    
    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Grad-CAM++
        cam = _get_gradcam()
        _, gradcam_overlay, _ = generate_gradcam(
            model, cam, img_tensor, target_class=pred_class_idx
        )
        
        # Convert Grad-CAM++ overlay to PIL and save
        gradcam_overlay_uint8 = (gradcam_overlay * 255).astype(np.uint8)
        gradcam_img = Image.fromarray(gradcam_overlay_uint8)
        gradcam_path = save_dir / "gradcam_overlay.png"
        save_pil_image(gradcam_img, gradcam_path)
        gradcam_overlay_path = str(gradcam_path)
        
        # Generate LIME
        # First, get denormalized image for LIME
        img_np = img_tensor[0].cpu().permute(1, 2, 0).numpy()
        mean = np.array(IMAGENET_MEAN).reshape(1, 1, 3)
        std = np.array(IMAGENET_STD).reshape(1, 1, 3)
        img_np = img_np * std + mean
        img_np = np.clip(img_np, 0, 1)
        
        explainer, lime_predict_fn = _get_lime()
        lime_overlay = generate_lime(
            img_np, explainer, lime_predict_fn, pred_class_idx
        )
        
        # Convert LIME overlay to PIL and save
        # LIME overlay is already in [0, 1] range
        lime_overlay_uint8 = (lime_overlay * 255).astype(np.uint8)
        lime_img = Image.fromarray(lime_overlay_uint8)
        lime_path = save_dir / "lime_overlay.png"
        save_pil_image(lime_img, lime_path)
        lime_overlay_path = str(lime_path)
        
        # Generate SHAP
        shap_explainer = _get_shap()
        _, shap_overlay, _ = generate_shap(
            model, shap_explainer, img_tensor, target_class=pred_class_idx
        )
        
        # Convert SHAP overlay to PIL and save
        shap_overlay_uint8 = (shap_overlay * 255).astype(np.uint8)
        shap_img = Image.fromarray(shap_overlay_uint8)
        shap_path = save_dir / "shap_overlay.png"
        save_pil_image(shap_img, shap_path)
        shap_overlay_path = str(shap_path)
    
    return {
        "pred_class_idx": pred_class_idx,
        "pred_class_name": pred_class_name,
        "confidence": confidence,
        "probs": [float(p) for p in probs],
        "gradcam_overlay_path": gradcam_overlay_path,
        "lime_overlay_path": lime_overlay_path,
        "shap_overlay_path": shap_overlay_path,
    }
