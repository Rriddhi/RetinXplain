"""Explainability module for Grad-CAM++, LIME, and SHAP.

This module provides functions to generate explainability visualizations
for single images. No batch processing or matplotlib dependencies.
"""

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from typing import Tuple, Callable, Optional

from pytorch_grad_cam import GradCAMPlusPlus
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from lime import lime_image
from skimage.segmentation import mark_boundaries, slic

import shap

from src.config import IMAGENET_MEAN, IMAGENET_STD, DEVICE
from src.data.transforms import validation_transform


def setup_gradcam(model: torch.nn.Module) -> GradCAMPlusPlus:
    """Setup Grad-CAM++ for the model.
    
    Target layer: last convolutional layer in ResNet50 layer4.
    
    Args:
        model: Trained ResNet50 model
    
    Returns:
        GradCAMPlusPlus instance configured for the model
    """
    # Ensure target layer has gradients enabled
    for param in model.layer4.parameters():
        param.requires_grad = True
    
    # Target layer: last convolutional layer in ResNet50
    target_layers = [model.layer4[-2]]
    
    # Initialize Grad-CAM++
    cam = GradCAMPlusPlus(model=model, target_layers=target_layers)
    return cam


def generate_gradcam(
    model: torch.nn.Module,
    cam: GradCAMPlusPlus,
    img_tensor: torch.Tensor,
    target_class: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate Grad-CAM++ heatmap and overlay.
    
    Args:
        model: Trained model
        cam: GradCAMPlusPlus instance
        img_tensor: Image tensor (1, 3, H, W) on device
        target_class: Class to explain. If None, uses predicted class.
    
    Returns:
        grayscale_cam: Heatmap array (H, W)
        overlay: Image with heatmap overlay (H, W, 3) as numpy array
        img_np: Denormalized original image (H, W, 3) as numpy array
    """
    # Get prediction if target_class not specified
    if target_class is None:
        with torch.no_grad():
            logits = model(img_tensor)
            target_class = logits.argmax(1).item()
    
    # Generate CAM
    targets = [ClassifierOutputTarget(target_class)]
    grayscale_cam = cam(input_tensor=img_tensor, targets=targets)
    grayscale_cam = grayscale_cam[0, :]  # Remove batch dimension
    
    # Denormalize image for visualization
    img_np = img_tensor[0].cpu().permute(1, 2, 0).numpy()
    mean = np.array(IMAGENET_MEAN).reshape(1, 1, 3)
    std = np.array(IMAGENET_STD).reshape(1, 1, 3)
    img_np = img_np * std + mean
    img_np = np.clip(img_np, 0, 1)
    
    # Create overlay
    overlay = show_cam_on_image(
        img_np.astype(np.float32),
        grayscale_cam,
        use_rgb=True,
        image_weight=0.6
    )
    
    return grayscale_cam, overlay, img_np


def setup_lime(
    model: torch.nn.Module
) -> Tuple[lime_image.LimeImageExplainer, Callable]:
    """Setup LIME explainer and prediction function.
    
    Args:
        model: Trained model
    
    Returns:
        explainer: LIME image explainer instance
        lime_predict_fn: Prediction function for LIME
    """
    explainer = lime_image.LimeImageExplainer()
    
    def lime_predict_fn(images_np: np.ndarray) -> np.ndarray:
        """Prediction function for LIME.
        
        Args:
            images_np: Array of images in numpy format (N, H, W, 3)
                      Values should be in [0, 1] range
        
        Returns:
            Probabilities array (N, num_classes)
        """
        model.eval()
        batch_tensors = []
        
        for img in images_np:
            # Normalize to [0, 1] if needed
            if img.max() > 1.0:
                img = img / 255.0
            
            # Convert to uint8 for PIL
            img_uint8 = (img * 255).astype(np.uint8)
            pil_img = Image.fromarray(img_uint8)
            
            # Apply validation transforms
            img_tensor = validation_transform(pil_img)
            batch_tensors.append(img_tensor)
        
        # Stack and move to device
        batch = torch.stack(batch_tensors).to(DEVICE)
        
        # Get predictions
        with torch.no_grad():
            logits = model(batch)
            probs = F.softmax(logits, dim=1).cpu().numpy()
        
        return probs
    
    return explainer, lime_predict_fn


def generate_lime(
    img_np: np.ndarray,
    explainer: lime_image.LimeImageExplainer,
    lime_predict_fn: Callable,
    pred_label: int,
    num_features: int = 6,
    num_samples: int = 1000
) -> np.ndarray:
    """Generate LIME explanation overlay.
    
    Args:
        img_np: Image as numpy array (H, W, 3) in [0, 1] range
        explainer: LIME image explainer instance
        lime_predict_fn: Prediction function for LIME
        pred_label: Predicted class label to explain
        num_features: Number of top features to highlight
        num_samples: Number of samples for LIME
    
    Returns:
        LIME overlay image (H, W, 3) as numpy array
    """
    def segmentation_fn(x: np.ndarray) -> np.ndarray:
        """Segmentation function for LIME."""
        return slic(x, n_segments=150, compactness=10, sigma=1)
    
    # Generate explanation
    explanation = explainer.explain_instance(
        img_np,
        lime_predict_fn,
        top_labels=5,
        num_samples=num_samples,
        hide_color=0,
        segmentation_fn=segmentation_fn,
    )
    
    # Get image and mask for predicted class
    temp, mask = explanation.get_image_and_mask(
        pred_label,
        positive_only=True,
        num_features=num_features,
        hide_rest=False,
    )
    
    # Normalize temp to [0, 1] if needed
    temp_vis = temp.astype(np.float32)
    if temp_vis.max() > 1.0:
        temp_vis /= 255.0
    
    # Create overlay with boundaries
    lime_overlay = mark_boundaries(temp_vis, mask)
    
    return lime_overlay


def setup_shap(
    model: torch.nn.Module,
    background_size: int = 10
) -> Tuple[shap.DeepExplainer, torch.Tensor]:
    """Setup SHAP DeepExplainer for the model.
    
    SHAP DeepExplainer requires a background dataset. This function creates
    a minimal background using random noise that approximates the input distribution.
    For better results, you can provide actual background images.
    
    Args:
        model: Trained model
        background_size: Number of background samples to generate (default: 10)
    
    Returns:
        explainer: SHAP DeepExplainer instance
        background: Background tensor (background_size, 3, H, W) for SHAP
    """
    # Create background dataset with random noise (approximates ImageNet distribution)
    # Using the same normalization as input images
    background = torch.randn(background_size, 3, 224, 224).to(DEVICE)
    
    # Normalize to ImageNet statistics
    mean_tensor = torch.tensor(IMAGENET_MEAN).view(1, 3, 1, 1).to(DEVICE)
    std_tensor = torch.tensor(IMAGENET_STD).view(1, 3, 1, 1).to(DEVICE)
    background = background * std_tensor + mean_tensor
    background = torch.clamp(background, 0, 1)
    
    # Initialize SHAP DeepExplainer
    explainer = shap.DeepExplainer(model, background)
    
    return explainer, background


def generate_shap(
    model: torch.nn.Module,
    explainer: shap.DeepExplainer,
    img_tensor: torch.Tensor,
    target_class: Optional[int] = None,
    num_samples: int = 100
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate SHAP explanation overlay.
    
    Args:
        model: Trained model
        explainer: SHAP DeepExplainer instance
        img_tensor: Image tensor (1, 3, H, W) on device
        target_class: Class to explain. If None, uses predicted class.
        num_samples: Number of samples for SHAP (not used for DeepExplainer,
                    but kept for API consistency)
    
    Returns:
        shap_heatmap: SHAP values heatmap (H, W) as numpy array
        overlay: Image with SHAP overlay (H, W, 3) as numpy array
        img_np: Denormalized original image (H, W, 3) as numpy array
    """
    # Get prediction if target_class not specified
    if target_class is None:
        with torch.no_grad():
            logits = model(img_tensor)
            target_class = logits.argmax(1).item()
    
    # Generate SHAP values
    # SHAP DeepExplainer expects input to be on the same device as the background
    shap_values = explainer.shap_values(img_tensor, check_additivity=False)
    
    # shap_values is a list of arrays, one per class
    # Get the values for the target class
    if isinstance(shap_values, list):
        shap_values_target = shap_values[target_class][0]  # Remove batch dimension
    else:
        shap_values_target = shap_values[target_class][0]
    
    # Aggregate across channels to get per-pixel importance
    # shap_values_target shape: (3, H, W) -> aggregate to (H, W)
    if len(shap_values_target.shape) == 3:
        # Sum across color channels to get total importance per pixel
        shap_heatmap = np.abs(shap_values_target).sum(axis=0)
    else:
        shap_heatmap = np.abs(shap_values_target)
    
    # Normalize heatmap to [0, 1] for visualization
    shap_heatmap = shap_heatmap - shap_heatmap.min()
    if shap_heatmap.max() > 0:
        shap_heatmap = shap_heatmap / shap_heatmap.max()
    
    # Denormalize image for visualization
    img_np = img_tensor[0].cpu().permute(1, 2, 0).numpy()
    mean = np.array(IMAGENET_MEAN).reshape(1, 1, 3)
    std = np.array(IMAGENET_STD).reshape(1, 1, 3)
    img_np = img_np * std + mean
    img_np = np.clip(img_np, 0, 1)
    
    # Create overlay similar to Grad-CAM
    overlay = show_cam_on_image(
        img_np.astype(np.float32),
        shap_heatmap,
        use_rgb=True,
        image_weight=0.6
    )
    
    return shap_heatmap, overlay, img_np
