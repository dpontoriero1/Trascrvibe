from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "Trascrvibe"

ALLOWED_EXTENSIONS = frozenset({
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".flac", ".opus",
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv", ".mpga",
})

SUPPORTED_MODELS = ("tiny", "base", "small", "medium", "large-v3")
SUPPORTED_PROVIDERS = ("faster-whisper", "demo")
DEFAULT_MAX_UPLOAD_MB = 5120


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    upload_dir: Path
    db_path: Path
    max_upload_mb: int
    default_model: str
    device: str
    compute_type: str
    default_language: str
    default_provider: str

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        env = os.environ if env is None else env

        model = env.get("TRSV_DEFAULT_MODEL", "base").strip().lower()
        if model not in SUPPORTED_MODELS:
            raise ValueError(
                f"Modello non valido: '{model}'. Valori ammessi: {', '.join(SUPPORTED_MODELS)}"
            )

        provider = env.get("TRSV_DEFAULT_PROVIDER", "faster-whisper").strip().lower()
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Provider non valido: '{provider}'. Valori ammessi: {', '.join(SUPPORTED_PROVIDERS)}"
            )

        language = env.get("TRSV_LANGUAGE", "auto").strip().lower() or "auto"

        data_dir = Path(env.get("TRSV_DATA_DIR", "data")).resolve()

        return cls(
            data_dir=data_dir,
            upload_dir=data_dir / "uploads",
            db_path=data_dir / "trascrvibe.sqlite",
            max_upload_mb=int(env.get("TRSV_MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB))),
            default_model=model,
            device=env.get("TRSV_DEVICE", "auto").strip().lower() or "auto",
            compute_type=env.get("TRSV_COMPUTE_TYPE", "auto").strip().lower() or "auto",
            default_language=language,
            default_provider=provider,
        )


def load_settings() -> Settings:
    return Settings.from_env()
