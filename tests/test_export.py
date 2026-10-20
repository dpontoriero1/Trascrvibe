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


def _make_done_job(client, app):
    resp = client.post(
        "/api/jobs",
        files={"file": ("intervista.mp3", io.BytesIO(b"0123456789"), "audio/mpeg")},
    )
    job_id = resp.json()["id"]
    app.state.manager.process_next()
    return job_id


def test_export_txt_srt_vtt(tmp_path):
    client, app = make_client(tmp_path)
    job_id = _make_done_job(client, app)

    r_txt = client.get(f"/api/jobs/{job_id}/export", params={"format": "txt"})
    assert r_txt.status_code == 200
    assert "[DEMO]" in r_txt.text
    assert 'attachment; filename="intervista.txt"' in r_txt.headers[
        "content-disposition"
    ]

    r_srt = client.get(f"/api/jobs/{job_id}/export", params={"format": "srt"})
    assert r_srt.status_code == 200
    assert "-->" in r_srt.text

    r_vtt = client.get(f"/api/jobs/{job_id}/export", params={"format": "vtt"})
    assert r_vtt.status_code == 200
    assert r_vtt.text.startswith("WEBVTT")


def test_export_invalid_format(tmp_path):
    client, app = make_client(tmp_path)
    job_id = _make_done_job(client, app)
    r = client.get(f"/api/jobs/{job_id}/export", params={"format": "pdf"})
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == "invalid_format"


def test_export_requires_done(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post(
        "/api/jobs",
        files={"file": ("a.mp3", io.BytesIO(b"0123456789"), "audio/mpeg")},
    )
    r = client.get(f"/api/jobs/{resp.json()['id']}/export", params={"format": "txt"})
    assert r.status_code == 409


def test_export_not_found(tmp_path):
    client, _ = make_client(tmp_path)
    r = client.get("/api/jobs/inesistente/export", params={"format": "txt"})
    assert r.status_code == 404
