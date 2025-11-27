"""Minimal FastAPI app exposing /health and /predict endpoints."""
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uuid
import os
from ..config import MODEL_PATH

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    # save uploaded file to uploads and return a dummy response
    uid = str(uuid.uuid4())
    out_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{uid}_original.png")
    with open(out_path, "wb") as f:
        f.write(await image.read())
    # stubbed prediction
    return JSONResponse({"id": uid, "label": 0, "probs": [1.0]})
