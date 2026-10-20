from __future__ import annotations

from pathlib import Path

from app.config import ALLOWED_EXTENSIONS


class UploadValidationError(Exception):
    """Errore di validazione con codice stabile (message_it/message_en nell'API)."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def validate_file_name(file_name: str) -> str:
    """Valida il nome file e restituisce l'estensione normalizzata."""
    name = (file_name or "").strip()
    if not name or name in (".", ".."):
        raise UploadValidationError("empty_filename")
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadValidationError("unsupported_extension")
    return ext


def validate_size(size_bytes: int, max_upload_mb: int) -> None:
    if size_bytes <= 0:
        raise UploadValidationError("empty_file")
    if size_bytes > max_upload_mb * 1024 * 1024:
        raise UploadValidationError("file_too_large")
