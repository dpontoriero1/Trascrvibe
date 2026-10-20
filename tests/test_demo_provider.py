from pathlib import Path

from app.providers.demo import DEMO_MARKER, DemoProvider


def test_demo_result_is_marked():
    result = DemoProvider().transcribe(Path("intervista.mp3"), language="it")
    assert result.is_demo is True
    assert result.provider_name == "demo"
    assert result.segments
    assert all(s.text.startswith(DEMO_MARKER) for s in result.segments)


def test_demo_language_and_timestamps():
    result_it = DemoProvider().transcribe(Path("a.wav"))
    assert result_it.language == "it"
    result_en = DemoProvider().transcribe(Path("a.wav"), language="en")
    assert result_en.language == "en"
    for result in (result_it, result_en):
        starts = [s.start for s in result.segments]
        assert starts == sorted(starts)
        assert all(s.end > s.start for s in result.segments)


def test_demo_never_claims_real_transcription():
    result = DemoProvider().transcribe(Path("x.mp4"), language="it")
    joined = "\n".join(s.text for s in result.segments)
    assert "Non è una trascrizione reale" in joined
