from __future__ import annotations

from typing import Iterable


def _parts(segments: Iterable) -> list[tuple[float, float, str]]:
    return [
        (float(s.start), float(s.end), (s.text or "").strip()) for s in segments
    ]


def _ms(seconds: float) -> int:
    return max(0, int(round(seconds * 1000)))


def _srt_time(seconds: float) -> str:
    ms = _ms(seconds)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _vtt_time(seconds: float) -> str:
    ms = _ms(seconds)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def export_txt(segments: Iterable) -> str:
    lines = [text for _, _, text in _parts(segments) if text]
    return "\n".join(lines) + ("\n" if lines else "")


def export_srt(segments: Iterable) -> str:
    blocks = []
    counter = 0
    for start, end, text in _parts(segments):
        if not text:
            continue
        counter += 1
        blocks.append(
            f"{counter}\n{_srt_time(start)} --> {_srt_time(end)}\n{text}\n"
        )
    return "\n".join(blocks)


def export_vtt(segments: Iterable) -> str:
    blocks = ["WEBVTT", ""]
    for start, end, text in _parts(segments):
        if not text:
            continue
        blocks.append(f"{_vtt_time(start)} --> {_vtt_time(end)}")
        blocks.append(text)
        blocks.append("")
    return "\n".join(blocks)
