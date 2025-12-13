from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
import datetime
from PIL import Image

from src.config import UPLOAD_ROOT
from src.inference.predictor import predict_with_explanations
from src.inference.llm_explainer import generate_explanation
from src.utils.image_io import save_pil_image

app = FastAPI(title="RetinXplain DR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving overlay images
app.mount("/static", StaticFiles(directory=str(UPLOAD_ROOT)), name="static")

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

    # 3) Generate LLM explanations
    explanations = generate_explanation(
        pred_class_idx=result["pred_class_idx"],
        pred_class_name=result["pred_class_name"],
        confidence=result["confidence"],
        probs=result["probs"]
    )

    # 4) Determine recommended action based on DR grade
    def get_recommended_action(dr_grade: int, confidence: float) -> tuple:
        """Returns (action, needs_review)"""
        if dr_grade == 0:
            return ("annual_screening", False)
        elif dr_grade == 1:
            return ("monitor_6_months", False)
        elif dr_grade == 2:
            return ("monitor_3_months", confidence < 0.7)
        elif dr_grade == 3:
            return ("urgent_referral", False)
        else:  # dr_grade == 4
            return ("urgent_referral", False)

    action, needs_review = get_recommended_action(result["pred_class_idx"], result["confidence"])

    # 5) Format probabilities as object with grade keys
    probabilities = {
        f"grade_{i}": float(prob) for i, prob in enumerate(result["probs"])
    }

    # 6) Convert overlay paths to relative paths and create URLs
    gradcam_url = None
    if result["gradcam_overlay_path"]:
        gradcam_abs = Path(result["gradcam_overlay_path"])
        gradcam_rel = str(gradcam_abs.relative_to(UPLOAD_ROOT))
        gradcam_url = f"/static/{gradcam_rel}"

    # 7) Format response to match frontend expectations
    return {
        "dr_grade": result["pred_class_idx"],
        "grade_name": result["pred_class_name"],
        "confidence": result["confidence"],
        "probabilities": probabilities,
        "action": action,
        "needs_review": needs_review,
        "clinician_summary": explanations["clinician_summary"],
        "patient_summary": explanations["patient_summary"],
        "gradcam_url": gradcam_url,
        "image_id": uid,
    }
