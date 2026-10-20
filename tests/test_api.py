import io

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.providers.demo import DemoProvider


def make_client(tmp_path):
    settings = Settings.from_env(
        env={"TRSV_DATA_DIR": str(tmp_path), "TRSV_DEFAULT_PROVIDER": "demo"}
    )
    app = create_app(settings=settings, provider=DemoProvider(), start_worker=False)
    return TestClient(app), app


def test_upload_and_result_flow(tmp_path):
    client, app = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("intervista.mp3", io.BytesIO(b"abc123"), "audio/mpeg")},
        data={"language": "it"},
    )
    assert resp.status_code == 201
    job = resp.json()
    assert job["status"] == "queued"
    assert job["is_demo"] is True

    app.state.manager.process_next()

    resp = client.get(f"/api/jobs/{job['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "done"
    assert body["is_demo"] is True
    assert body["segments"]


def test_unsupported_extension_rejected(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("virus.exe", io.BytesIO(b"x" * 10), "application/octet-stream")},
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "unsupported_extension"


def test_empty_file_rejected(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("a.wav", io.BytesIO(b""), "audio/wav")},
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "empty_file"


def test_invalid_model_rejected(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("a.mp3", io.BytesIO(b"x" * 10), "audio/mpeg")},
        data={"model": "gigante"},
    )
    assert resp.status_code == 422


def test_delete_job(tmp_path):
    client, app = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("a.mp3", io.BytesIO(b"x" * 10), "audio/mpeg")},
    )
    job_id = resp.json()["id"]
    resp = client.delete(f"/api/jobs/{job_id}")
    assert resp.status_code == 204
    resp = client.get(f"/api/jobs/{job_id}")
    assert resp.status_code == 404


def test_config_and_health(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/health").json()["status"] == "ok"
    config = client.get("/api/config").json()
    assert config["is_demo"] is True
    assert "base" in config["models"]
