from typing import Dict
from PIL import Image
import torch

from src.utils.paths import get_path
from src.models.classification.resnet_classifier import ResNetDRClassifier
from src.explainability.grad_cam import GradCAM
from src.explainability.overlays import overlay_heatmap_on_image
from src.explainability.summaries import summarize_lesions
from src.llm.explainer import get_explanation

# TODO: load your UNet later
# from src.models.segmentation.unet import UNet

_device = "cuda" if torch.cuda.is_available() else "cpu"

# Lazy-loaded globals
_classifier = None
_grad_cam = None

def _load_classifier():
    global _classifier, _grad_cam
    if _classifier is None:
        model = ResNetDRClassifier(num_classes=5, pretrained=False)
        ckpt_path = get_path("models", "aptos", "best_resnet50.pt")
        model.load_state_dict(torch.load(ckpt_path, map_location=_device))
        model.eval().to(_device)
        _classifier = model
        _grad_cam = GradCAM(model, target_layer_name="backbone.layer4")  # adjust later

def run_full_pipeline(image: Image.Image) -> Dict:
    _load_classifier()

    # Preprocess
    image_resized = image.resize((512, 512))
    img_tensor = torch.from_numpy(
        ( ( ( (torch.ByteTensor(torch.ByteStorage.from_buffer(image_resized.tobytes())).view(512, 512, 3).numpy()).astype("float32") / 255.0 ).transpose(2,0,1) ))
    )  # <-- we can simplify later; for now treat as TODO
    img_tensor = img_tensor.unsqueeze(0).to(_device)

    with torch.no_grad():
        logits = _classifier(img_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        pred_idx = int(probs.argmax())
        confidence = float(probs[pred_idx])

    # TODO: map pred_idx -> DR grade string
    dr_grade = f"class_{pred_idx}"

    # Grad-CAM heatmap
    cam = _grad_cam.generate(img_tensor, class_idx=pred_idx)
    heatmap_overlay = overlay_heatmap_on_image(image_resized, cam)

    # TODO: run U-Net, get mask_dict
    mask_dict = {
        "microaneurysms": None,  # placeholder
    }
    lesion_summary = "Lesion segmentation model not integrated yet."

    explanation = get_explanation(dr_grade, confidence, lesion_summary)

    return {
        "dr_grade": dr_grade,
        "confidence": confidence,
        "probabilities": probs.tolist(),
        "gradcam_overlay": heatmap_overlay,
        "explanation": explanation,
    }
