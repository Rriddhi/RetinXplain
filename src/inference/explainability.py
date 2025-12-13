"""Explainability module for Grad-CAM.

This module provides functions to generate Grad-CAM explainability visualizations
for single images using a custom implementation.
"""

import numpy as np
import torch
import cv2
from typing import Tuple, Optional
from PIL import Image

from src.config import IMAGENET_MEAN, IMAGENET_STD


class GradCAM:
    """
    Grad-CAM (Gradient-weighted Class Activation Mapping) for model explainability.
    Generates heatmaps showing which regions of the image influenced the prediction.
    """
    
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks to capture activations and gradients
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        """Save activations from forward pass."""
        self.activations = output.detach()
    
    def save_gradient(self, module, grad_input, grad_output):
        """Save gradients from backward pass."""
        self.gradients = grad_output[0].detach()
    
    def generate_cam(self, input_tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        """
        Generate Class Activation Map for the specified class.
        
        Args:
            input_tensor: Input image tensor (1, 3, H, W)
            class_idx: Target class index
        
        Returns:
            cam: Numpy array of heatmap (H, W) normalized to [0, 1]
        """
        self.model.eval()
        self.model.zero_grad()
        
        # Forward pass
        output = self.model(input_tensor)
        
        # Backward pass for target class
        target = output[0, class_idx]
        target.backward()
        
        # Get gradients and activations
        gradients = self.gradients[0].cpu().numpy()
        activations = self.activations[0].cpu().numpy()
        
        # Calculate weights (global average pooling of gradients)
        weights = np.mean(gradients, axis=(1, 2))
        
        # Generate CAM
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # Apply ReLU
        cam = np.maximum(cam, 0)
        
        # Resize to input image size
        cam = cv2.resize(cam, (input_tensor.shape[3], input_tensor.shape[2]))
        
        # Normalize to [0, 1]
        if cam.max() > 0:
            cam = cam / cam.max()
        
        return cam


def setup_gradcam(model: torch.nn.Module) -> GradCAM:
    """
    Setup Grad-CAM for the model.
    Target layer: last convolutional layer in ResNet50 layer4.
    
    Args:
        model: ResNet50 model
    
    Returns:
        GradCAM instance
    """
    # Target layer: last convolutional layer in ResNet50
    target_layer = model.layer4[-1].conv2
    
    # Ensure target layer has gradients enabled
    for param in model.layer4.parameters():
        param.requires_grad = True
    
    # Initialize Grad-CAM
    cam = GradCAM(model, target_layer)
    return cam


def generate_gradcam(
    model: torch.nn.Module,
    cam: GradCAM,
    img_tensor: torch.Tensor,
    target_class: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate Grad-CAM heatmap and overlay.
    
    Args:
        model: Trained model
        cam: GradCAM instance
        img_tensor: Image tensor (1, 3, H, W) on device
        target_class: Class to explain. If None, uses predicted class.
    
    Returns:
        grayscale_cam: Heatmap array (H, W) in [0, 1]
        overlay: Image with heatmap overlay (H, W, 3) as numpy array
        img_np: Denormalized original image (H, W, 3) as numpy array
    """
    # Get prediction if target_class not specified
    if target_class is None:
        with torch.no_grad():
            logits = model(img_tensor)
            target_class = logits.argmax(1).item()
    
    # Generate CAM
    grayscale_cam = cam.generate_cam(img_tensor, target_class)
    
    # Denormalize image for visualization
    img_np = img_tensor[0].cpu().permute(1, 2, 0).numpy()
    mean = np.array(IMAGENET_MEAN).reshape(1, 1, 3)
    std = np.array(IMAGENET_STD).reshape(1, 1, 3)
    img_np = img_np * std + mean
    img_np = np.clip(img_np, 0, 1)
    
    # Convert to uint8 for OpenCV
    img_uint8 = (img_np * 255).astype(np.uint8)
    
    # Create heatmap using JET colormap
    heatmap = cv2.applyColorMap(np.uint8(255 * grayscale_cam), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    # Create overlay (0.6 original image, 0.4 heatmap)
    overlay = cv2.addWeighted(img_uint8, 0.6, heatmap, 0.4, 0)
    
    # Convert overlay to [0, 1] range for consistency
    overlay = overlay.astype(np.float32) / 255.0
    
    return grayscale_cam, overlay, img_np
