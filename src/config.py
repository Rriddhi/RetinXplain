import os

# Simple config placeholders. Edit as needed.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(ROOT_DIR, "models", "dr_efficientnet_b4_best.pt"))
IMAGE_SIZE = (512, 512)
CLASS_NAMES = ["No_DR", "Mild", "Moderate", "Severe", "Proliferative"]
