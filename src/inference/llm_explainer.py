import os

from src.config import CLASS_NAMES

def generate_explanation(prediction, clinical_notes: str | None = None) -> str:
    """
    prediction: dict from predict_image()
    clinical_notes: optional free-text from clinician / form
    """
    class_name = prediction["class_name"]
    probs = prediction["probabilities"]

    # For now you can stub this out with a template; later call OpenAI / Anthropic.
    explanation = (
        f"The model's prediction is **{class_name} diabetic retinopathy**. "
        f"It assigns the following probabilities: {probs}. "
        "Based on these probabilities and typical DR findings, the image is most consistent "
        "with lesions at this severity level. (Future: tie to Grad-CAM regions + ICD-10 code.)"
    )
    return explanation
