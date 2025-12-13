from pathlib import Path
import torch
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ResNet50 model configuration
RESNET50_MODEL_PATH = PROJECT_ROOT / "models" / "resnet50_best_cleaned.pt"
UPLOAD_ROOT = PROJECT_ROOT / "uploads"

# Image configuration
IMG_SIZE = 224  # ResNet50 standard input size
IMG_RESIZE = 256  # Resize before center crop
NUM_CLASSES = 5
CLASS_NAMES = {
    0: "No DR",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative DR"
}

# ImageNet normalization constants
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Device selection (prioritize MPS for Apple Silicon, then CUDA, then CPU)
if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")

# LLM config (fill in from .env)
LLM_PROVIDER = "anthropic"   # Options: "anthropic" or "openai"
LLM_MODEL_NAME = "claude-3-5-sonnet-20241022"  # Anthropic model name
