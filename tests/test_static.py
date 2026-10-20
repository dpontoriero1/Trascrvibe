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


def test_index_served(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Trascrvibe" in resp.text


def test_media_served_with_range(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("a.mp3", io.BytesIO(b"0123456789"), "audio/mpeg")},
    )
    job_id = resp.json()["id"]

    r = client.get(f"/api/jobs/{job_id}/media")
    assert r.status_code == 200
    assert r.content == b"0123456789"

    r2 = client.get(f"/api/jobs/{job_id}/media", headers={"Range": "bytes=2-5"})
    assert r2.status_code == 206
    assert r2.content == b"2345"
    assert r2.headers["content-range"] == "bytes 2-5/10"


def test_media_not_found(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/jobs/inesistente/media").status_code == 404


def test_update_segments(tmp_path):
    client, app = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("a.mp3", io.BytesIO(b"0123456789"), "audio/mpeg")},
    )
    job_id = resp.json()["id"]
    app.state.manager.process_next()

    payload = {"segments": [{"start": 0.0, "end": 2.0, "text": "testo corretto"}]}
    r = client.put(f"/api/jobs/{job_id}/segments", json=payload)
    assert r.status_code == 200
    assert r.json()["count"] == 1

    body = client.get(f"/api/jobs/{job_id}").json()
    assert body["segments"][0]["text"] == "testo corretto"


def test_update_segments_requires_done(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("a.mp3", io.BytesIO(b"0123456789"), "audio/mpeg")},
    )
    job_id = resp.json()["id"]
    r = client.put(
        f"/api/jobs/{job_id}/segments", json={"segments": []}
    )
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "not_editable"
