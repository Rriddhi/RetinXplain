"""Model loader for ResNet50 Diabetic Retinopathy classification.

This module provides functions to build and load the ResNet50 model
for inference-only prediction. No training code is included.
"""

import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path

from src.config import RESNET50_MODEL_PATH, NUM_CLASSES, DEVICE


def build_resnet50_dr(num_classes: int = NUM_CLASSES) -> nn.Module:
    """Build ResNet50 model architecture for DR classification.
    
    This matches the exact architecture used during training:
    - Pretrained ResNet50 with ImageNet weights
    - Final FC layer replaced for num_classes classification
    
    Args:
        num_classes: Number of output classes (default: 5)
    
    Returns:
        ResNet50 model with modified classifier head
    """
    # Load pretrained ResNet50
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    
    # Replace final fully connected layer for classification
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    
    return model


def load_resnet50_dr_model() -> nn.Module:
    """Load ResNet50 DR model from best model weights.
    
    Always loads from the best model path defined in config
    (models/resnet50_best_cleaned.pt). Does not load from checkpoints.
    
    Returns:
        Loaded model in eval mode, moved to appropriate device
    
    Raises:
        FileNotFoundError: If the best model file does not exist
    """
    model_path = RESNET50_MODEL_PATH
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Best model weights not found at {model_path}. "
            "Please ensure the model file exists."
        )
    
    # Build model architecture
    model = build_resnet50_dr(num_classes=NUM_CLASSES)
    
    # Load weights from best model (not checkpoint)
    state_dict = torch.load(model_path, map_location=DEVICE)
    model.load_state_dict(state_dict)
    
    # Set to evaluation mode and move to device
    model.eval()
    model = model.to(DEVICE)
    
    return model
