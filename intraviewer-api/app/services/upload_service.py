"""Image uploads (profile photos, company logos).

Validates by file signature (magic bytes), not by the client-supplied
content-type or extension.
"""
import os
import uuid
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import ApiError

_PUBLIC_PREFIX = "/static/uploads"


def _detect_image_ext(head: bytes) -> Optional[str]:
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head[:3] == b"\xff\xd8\xff":
        return "jpg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


async def save_image(file: UploadFile, kind: str) -> str:
    max_bytes = settings.MAX_IMAGE_UPLOAD_BYTES
    data = await file.read(max_bytes + 1)
    if not data:
        raise ApiError(400, "The selected file is empty.", "INVALID_FILE", errors={"file": "Empty file"})
    if len(data) > max_bytes:
        mb = max_bytes // (1024 * 1024)
        raise ApiError(413, f"Image must be {mb} MB or smaller.", "FILE_TOO_LARGE",
                       errors={"file": f"Max {mb} MB"})
    ext = _detect_image_ext(data[:16])
    if ext is None:
        raise ApiError(400, "Upload a PNG, JPG or WEBP image.", "INVALID_FILE_TYPE",
                       errors={"file": "Unsupported file type"})

    folder = os.path.join(settings.UPLOAD_DIR, kind)
    os.makedirs(folder, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(folder, filename), "wb") as fh:
        fh.write(data)
    return f"{_PUBLIC_PREFIX}/{kind}/{filename}"


def delete_image(public_path: Optional[str]) -> None:
    """Delete a previously uploaded file; ignores anything outside our upload dir."""
    if not public_path or not public_path.startswith(_PUBLIC_PREFIX + "/"):
        return
    rel = public_path[len(_PUBLIC_PREFIX) + 1:]
    base = os.path.realpath(settings.UPLOAD_DIR)
    target = os.path.realpath(os.path.join(base, rel))
    if target.startswith(base + os.sep) and os.path.isfile(target):
        try:
            os.remove(target)
        except OSError:
            pass
