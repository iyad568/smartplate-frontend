"""
Local file storage utility.
Saves uploaded files under  <project_root>/uploads/<subfolder>/
and returns a publicly accessible URL served by FastAPI's StaticFiles mount.
"""
import uuid
import os
from pathlib import Path
from fastapi import UploadFile

from app.core.config import get_settings

# Root of the uploads directory — sits next to main.py
UPLOADS_ROOT = Path(__file__).resolve().parents[2] / "uploads"


def _ensure_dir(subfolder: str) -> Path:
    target = UPLOADS_ROOT / subfolder
    target.mkdir(parents=True, exist_ok=True)
    return target


async def save_upload(file: UploadFile, subfolder: str) -> str:
    """
    Save *file* under uploads/<subfolder>/ with a unique name.
    Returns the full public URL, e.g. http://localhost:8002/uploads/vignettes/abc123.jpg
    """
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = _ensure_dir(subfolder) / filename

    contents = await file.read()
    dest.write_bytes(contents)

    settings = get_settings()
    return f"{settings.BACKEND_URL}/uploads/{subfolder}/{filename}"
