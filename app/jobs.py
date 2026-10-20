from __future__ import annotations

import threading
from pathlib import Path

from app.providers import build_provider
from app.providers.base import TranscriptionError, TranscriptionProvider
from app.storage import JobStore


class JobManager:
    """Coda lavori con worker in background (un lavoro alla volta, uso locale)."""

    def __init__(
        self,
        store: JobStore,
        settings,
        provider: TranscriptionProvider | None = None,
        start_worker: bool = True,
    ):
        self.store = store
        self.settings = settings
        self.provider = provider or build_provider(settings)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        if start_worker:
            self._thread = threading.Thread(
                target=self._worker_loop, name="trascrvibe-worker", daemon=True
            )
            self._thread.start()

    def enqueue(self, *, original_name: str, stored_path: Path, language: str, model: str) -> dict:
        return self.store.create_job(
            original_name=original_name,
            stored_path=stored_path,
            language=language,
            model=model,
            provider=self.provider.name,
        )

    def process_next(self) -> bool:
        """Elabora il primo lavoro in coda. Restituisce False se la coda è vuota."""
        job = self.store.next_queued_job()
        if job is None:
            return False
        self._run(job)
        return True

    def shutdown(self) -> None:
        self._stop.set()

    def _worker_loop(self) -> None:
        while not self._stop.is_set():
            if not self.process_next():
                self._stop.wait(0.5)

    def _run(self, job: dict) -> None:
        job_id = job["id"]
        self.store.update_job(job_id, status="processing", progress=0.0, error=None)
        try:
            language = job["language"]
            if language in ("", "auto", None):
                language = None
            result = self.provider.transcribe(
                Path(job["stored_path"]), language=language, model_size=job["model"]
            )
            if not result.segments and not result.is_demo:
                self.store.update_job(
                    job_id,
                    status="failed",
                    error="Trascrizione vuota: nessun parlato rilevato nel file.",
                )
                return
            self.store.save_segments(job_id, result.segments)
            self.store.update_job(
                job_id,
                status="done",
                progress=1.0,
                language=result.language,
                provider=result.provider_name,
                is_demo=int(result.is_demo),
                error=None,
            )
        except TranscriptionError as exc:
            self.store.update_job(job_id, status="failed", error=str(exc))
        except Exception as exc:
            self.store.update_job(job_id, status="failed", error=f"{type(exc).__name__}: {exc}")
