from __future__ import annotations

import mimetypes
import re
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import SUPPORTED_MODELS, Settings, load_settings
from app.jobs import JobManager
from app.providers.base import Segment, TranscriptionProvider
from app.storage import JobStore
from app.validation import UploadValidationError, validate_file_name

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

ERROR_MESSAGES = {
    "empty_filename": ("Nome file mancante.", "Missing file name."),
    "unsupported_extension": ("Formato file non supportato.", "Unsupported file format."),
    "empty_file": ("Il file è vuoto o illeggibile.", "The file is empty or unreadable."),
    "file_too_large": (
        "Il file supera la dimensione massima consentita.",
        "The file exceeds the maximum allowed size.",
    ),
    "not_found": ("Lavoro non trovato.", "Job not found."),
    "invalid_model": ("Modello non valido.", "Invalid model."),
    "not_editable": (
        "La trascrizione non è ancora pronta.",
        "The transcript is not ready yet.",
    ),
}


def _error(status_code: int, code: str):
    it, en = ERROR_MESSAGES[code]
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message_it": it, "message_en": en},
    )


def _job_out(job: dict) -> dict:
    out = dict(job)
    out["is_demo"] = bool(out.get("is_demo"))
    return out


class SegmentIn(BaseModel):
    start: float
    end: float
    text: str


class SegmentsIn(BaseModel):
    segments: list[SegmentIn]


def create_app(
    settings: Settings | None = None,
    provider: TranscriptionProvider | None = None,
    start_worker: bool = True,
) -> FastAPI:
    settings = settings or load_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    store = JobStore(settings.db_path)
    manager = JobManager(store, settings, provider=provider, start_worker=start_worker)

    app = FastAPI(title="Trascrvibe")
    app.state.manager = manager
    app.state.settings = settings

    @app.get("/api/health")
    def health():
        return {"status": "ok", "app": "Trascrvibe"}

    @app.get("/api/config")
    def config():
        return {
            "max_upload_mb": settings.max_upload_mb,
            "models": list(SUPPORTED_MODELS),
            "default_model": settings.default_model,
            "default_language": settings.default_language,
            "provider": manager.provider.name,
            "is_demo": manager.provider.is_demo,
        }

    @app.post("/api/jobs", status_code=201)
    def create_job(
        file: UploadFile = File(...),
        language: str = Form("auto"),
        model: str = Form(""),
    ):
        model = (model or "").strip() or settings.default_model
        if model not in SUPPORTED_MODELS:
            _error(422, "invalid_model")
        try:
            ext = validate_file_name(file.filename or "")
        except UploadValidationError as exc:
            _error(422, exc.code)

        job_id = uuid.uuid4().hex
        stored_path = settings.upload_dir / f"{job_id}{ext}"
        max_bytes = settings.max_upload_mb * 1024 * 1024
        size = 0
        with open(stored_path, "wb") as out:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                out.write(chunk)
        file.file.close()

        if size == 0:
            stored_path.unlink(missing_ok=True)
            _error(422, "empty_file")
        if size > max_bytes:
            stored_path.unlink(missing_ok=True)
            _error(413, "file_too_large")

        job = manager.enqueue(
            original_name=file.filename,
            stored_path=stored_path,
            language=(language or "auto").strip().lower() or "auto",
            model=model,
        )
        return _job_out(job)

    @app.get("/api/jobs")
    def list_jobs():
        return [_job_out(j) for j in store.list_jobs()]

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str):
        job = store.get_job(job_id)
        if job is None:
            _error(404, "not_found")
        out = _job_out(job)
        if out["status"] == "done":
            out["segments"] = store.get_segments(job_id)
        return out

    @app.get("/api/jobs/{job_id}/media")
    def get_media(job_id: str, request: Request):
        job = store.get_job(job_id)
        if job is None:
            _error(404, "not_found")
        stored = Path(job["stored_path"])
        if not stored.is_file():
            _error(404, "not_found")
        media_type = mimetypes.guess_type(stored.name)[0] or "application/octet-stream"
        size = stored.stat().st_size
        range_header = request.headers.get("range")
        if range_header:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
            if match:
                start_s, end_s = match.groups()
                if start_s == "" and end_s == "":
                    start, end = 0, size - 1
                elif start_s == "":
                    length = min(int(end_s), size)
                    start, end = size - length, size - 1
                else:
                    start = int(start_s)
                    end = min(int(end_s), size - 1) if end_s else size - 1
                if start < 0 or start > end or start >= size:
                    return Response(
                        status_code=416,
                        headers={"Content-Range": f"bytes */{size}"},
                    )
                with open(stored, "rb") as f:
                    f.seek(start)
                    data = f.read(end - start + 1)
                return Response(
                    content=data,
                    status_code=206,
                    media_type=media_type,
                    headers={
                        "Content-Range": f"bytes {start}-{end}/{size}",
                        "Accept-Ranges": "bytes",
                    },
                )
        return FileResponse(
            stored, media_type=media_type, headers={"Accept-Ranges": "bytes"}
        )

    @app.put("/api/jobs/{job_id}/segments")
    def update_segments(job_id: str, payload: SegmentsIn):
        job = store.get_job(job_id)
        if job is None:
            _error(404, "not_found")
        if job["status"] != "done":
            _error(409, "not_editable")
        store.save_segments(
            job_id, [Segment(s.start, s.end, s.text) for s in payload.segments]
        )
        return {"ok": True, "count": len(payload.segments)}

    @app.delete("/api/jobs/{job_id}", status_code=204)
    def delete_job(job_id: str):
        job = store.get_job(job_id)
        if job is None:
            _error(404, "not_found")
        stored = Path(job["stored_path"])
        if stored.exists():
            stored.unlink()
        store.delete_job(job_id)

    if WEB_DIR.is_dir() and (WEB_DIR / "index.html").is_file():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

    return app
