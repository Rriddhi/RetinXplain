from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import datetime
from PIL import Image

from src.config import UPLOAD_ROOT
from src.inference.predictor import predict_with_explanations
from src.utils.image_io import save_pil_image

app = FastAPI(title="RetinXplain DR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/dr/predict")
async def predict_dr(file: UploadFile = File(...)):
    """Predict DR classification with explainability visualizations.
    
    This endpoint uses the ResNet50 model trained for DR classification.
    It returns predictions along with Grad-CAM++ and LIME overlays.
    
    Args:
        file: Uploaded fundus image (multipart/form-data)
    
    Returns:
        JSON response with:
        - pred_class_idx: Predicted class index (0-4)
        - pred_class_name: Predicted class name
        - confidence: Confidence score
        - probs: List of probabilities for all 5 classes
        - gradcam_overlay_path: Relative path to Grad-CAM++ overlay
        - lime_overlay_path: Relative path to LIME overlay
        - shap_overlay_path: Relative path to SHAP overlay
    """
    # 1) Save original upload
    today = datetime.date.today().isoformat()
    folder = UPLOAD_ROOT / today
    folder.mkdir(parents=True, exist_ok=True)

    uid = uuid.uuid4().hex
    original_path = folder / f"{uid}_original.png"

    # Load and save image
    img = Image.open(file.file).convert("RGB")
    save_pil_image(img, original_path)

    # 2) Run prediction with explanations
    result = predict_with_explanations(original_path, save_dir=folder)

    # 3) Update paths to be relative to UPLOAD_ROOT
    if result["gradcam_overlay_path"]:
        gradcam_abs = Path(result["gradcam_overlay_path"])
        result["gradcam_overlay_path"] = str(gradcam_abs.relative_to(UPLOAD_ROOT))
    
    if result["lime_overlay_path"]:
        lime_abs = Path(result["lime_overlay_path"])
        result["lime_overlay_path"] = str(lime_abs.relative_to(UPLOAD_ROOT))
    
    if result["shap_overlay_path"]:
        shap_abs = Path(result["shap_overlay_path"])
        result["shap_overlay_path"] = str(shap_abs.relative_to(UPLOAD_ROOT))

    return {
        "pred_class_idx": result["pred_class_idx"],
        "pred_class_name": result["pred_class_name"],
        "confidence": result["confidence"],
        "probs": result["probs"],
        "artifacts": {
            "original_image_path": str(original_path.relative_to(UPLOAD_ROOT)),
            "gradcam_overlay_path": result["gradcam_overlay_path"],
            "lime_overlay_path": result["lime_overlay_path"],
            "shap_overlay_path": result["shap_overlay_path"],
        },
    }
