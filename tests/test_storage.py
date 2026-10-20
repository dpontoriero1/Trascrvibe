from pathlib import Path

from app.providers.base import Segment
from app.storage import JobStore


def make_store(tmp_path) -> JobStore:
    return JobStore(tmp_path / "test.sqlite")


def make_job(store):
    return store.create_job(
        original_name="a.mp3",
        stored_path=Path("/fake/a.mp3"),
        language="it",
        model="base",
        provider="demo",
    )


def test_create_and_get_job(tmp_path):
    store = make_store(tmp_path)
    job = make_job(store)
    assert job["status"] == "queued"
    assert job["is_demo"] == 1
    fetched = store.get_job(job["id"])
    assert fetched["original_name"] == "a.mp3"
    assert store.get_job("inesistente") is None


def test_update_and_list(tmp_path):
    store = make_store(tmp_path)
    job = make_job(store)
    store.update_job(job["id"], status="done", progress=1.0)
    jobs = store.list_jobs()
    assert jobs[0]["status"] == "done"


def test_next_queued_orders_by_time(tmp_path):
    store = make_store(tmp_path)
    first = make_job(store)
    second = make_job(store)
    assert store.next_queued_job()["id"] == first["id"]
    store.update_job(first["id"], status="processing")
    assert store.next_queued_job()["id"] == second["id"]


def test_segments_roundtrip_and_delete(tmp_path):
    store = make_store(tmp_path)
    job = make_job(store)
    store.save_segments(
        job["id"],
        [Segment(0.0, 1.5, "ciao"), Segment(1.5, 3.0, "mondo")],
    )
    segs = store.get_segments(job["id"])
    assert len(segs) == 2
    assert segs[0]["text"] == "ciao"
    assert segs[1]["start"] == 1.5

    store.save_segments(job["id"], [Segment(0.0, 1.0, "solo")])
    assert len(store.get_segments(job["id"])) == 1

    assert store.delete_job(job["id"]) is True
    assert store.get_job(job["id"]) is None
    assert store.get_segments(job["id"]) == []
