from app.exporters import export_srt, export_txt, export_vtt
from app.providers.base import Segment


def segs(*args):
    return [Segment(a, b, c) for a, b, c in args]


def test_srt_format_and_numbering():
    out = export_srt(segs((0.0, 2.5, "ciao"), (2.5, 4.0, "mondo")))
    lines = out.splitlines()
    assert lines[0] == "1"
    assert lines[1] == "00:00:00,000 --> 00:00:02,500"
    assert lines[2] == "ciao"
    assert lines[4] == "2"
    assert lines[5] == "00:00:02,500 --> 00:00:04,000"
    assert lines[6] == "mondo"


def test_srt_hours_and_milliseconds():
    out = export_srt(segs((3661.5, 3662.25, "x")))
    assert "01:01:01,500 --> 01:01:02,250" in out


def test_vtt_header_and_format():
    out = export_vtt(segs((0.0, 1.0, "a"), (1.0, 2.0, "b")))
    assert out.startswith("WEBVTT")
    assert "00:00:00.000 --> 00:00:01.000" in out
    assert "00:00:01.000 --> 00:00:02.000" in out


def test_txt_joins_text():
    out = export_txt(segs((0.0, 1.0, "uno "), (1.0, 2.0, ""), (2.0, 3.0, "due")))
    assert out == "uno\ndue\n"


def test_empty_segments():
    assert export_txt([]) == ""
    assert export_srt([]) == ""
    assert export_vtt([]).startswith("WEBVTT")


def test_empty_text_skipped_in_srt():
    out = export_srt(segs((0.0, 1.0, "  "), (1.0, 2.0, "ok")))
    lines = out.splitlines()
    assert lines[0] == "1"
    assert "ok" in out
