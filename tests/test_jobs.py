from app.config import Settings
from app.jobs import JobManager
from app.providers.demo import DemoProvider
from app.storage import JobStore


class BrokenProvider(DemoProvider):
    def transcribe(self, media_path, language=None, model_size=None):
        raise RuntimeError("boom")


def make_manager(tmp_path, provider=None):
    settings = Settings.from_env(
        env={"TRSV_DATA_DIR": str(tmp_path), "TRSV_DEFAULT_PROVIDER": "demo"}
    )
    store = JobStore(settings.db_path)
    return JobManager(
        store, settings, provider=provider or DemoProvider(), start_worker=False
    )


def test_demo_job_completes(tmp_path):
    manager = make_manager(tmp_path)
    job = manager.enqueue(
        original_name="a.mp3",
        stored_path=tmp_path / "a.mp3",
        language="it",
        model="base",
    )
    assert job["status"] == "queued"

    assert manager.process_next() is True
    done = manager.store.get_job(job["id"])
    assert done["status"] == "done"
    assert done["is_demo"] == 1
    segments = manager.store.get_segments(job["id"])
    assert segments
    assert all(s["text"].startswith("[DEMO]") for s in segments)


def test_failure_marks_job_failed(tmp_path):
    manager = make_manager(tmp_path, provider=BrokenProvider())
    job = manager.enqueue(
        original_name="a.mp3",
        stored_path=tmp_path / "a.mp3",
        language="it",
        model="base",
    )
    manager.process_next()
    failed = manager.store.get_job(job["id"])
    assert failed["status"] == "failed"
    assert "boom" in failed["error"]


def test_process_next_empty_queue(tmp_path):
    manager = make_manager(tmp_path)
    assert manager.process_next() is False
