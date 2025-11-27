"""Helpers for saving uploads and generating UUID-based paths."""
import os
import uuid

def save_upload_bytes(data: bytes, upload_dir: str, prefix: str = ""):
    os.makedirs(upload_dir, exist_ok=True)
    uid = str(uuid.uuid4())
    filename = f"{uid}_{prefix}.png" if prefix else f"{uid}.png"
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path
