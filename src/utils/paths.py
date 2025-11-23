import os

# You can tweak this if needed in Colab
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_path(*parts: str) -> str:
    """Join parts relative to project root."""
    return os.path.join(PROJECT_ROOT, *parts)