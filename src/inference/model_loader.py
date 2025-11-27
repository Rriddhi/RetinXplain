"""Model loader stub: build EfficientNet-B4 and load weights.

Replace with the exact model construction code you use in Colab.
"""
import os
import torch

def load_model(path: str, device="cpu"):
    # Placeholder: users should instantiate their model here and load_state_dict
    model = torch.nn.Identity()
    try:
        if path and os.path.exists(path):
            model.load_state_dict(torch.load(path, map_location=device))
    except Exception:
        pass
    model.to(device)
    model.eval()
    return model
