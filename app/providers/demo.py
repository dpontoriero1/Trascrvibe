from __future__ import annotations

from pathlib import Path

from .base import Segment, TranscriptResult, TranscriptionProvider

DEMO_MARKER = "[DEMO]"


class DemoProvider(TranscriptionProvider):
    """Provider di sviluppo: NON trascrive davvero.

    Restituisce un testo dimostrativo sempre marcato [DEMO], utile per
    sviluppare e testare l'applicazione senza modelli installati.
    """

    name = "demo"
    is_demo = True
    supports_language_detection = False

    def transcribe(
        self,
        media_path: Path,
        language: str | None = None,
        model_size: str | None = None,
    ) -> TranscriptResult:
        lang = "en" if language == "en" else "it"
        file_name = Path(media_path).name

        if lang == "en":
            texts = (
                f"{DEMO_MARKER} Trascrvibe demo output for '{file_name}'.",
                f"{DEMO_MARKER} This is not a real transcription; the faster-whisper engine is not installed or active.",
                f"{DEMO_MARKER} Provider: demo.",
            )
        else:
            texts = (
                f"{DEMO_MARKER} Output demo di Trascrvibe per '{file_name}'.",
                f"{DEMO_MARKER} Non è una trascrizione reale; il motore faster-whisper non è installato o attivo.",
                f"{DEMO_MARKER} Provider: demo.",
            )

        segments = tuple(
            Segment(start=float(i), end=float(i) + 1.0, text=text)
            for i, text in enumerate(texts)
        )
        return TranscriptResult(
            segments=segments,
            language=lang,
            provider_name=self.name,
            is_demo=True,
        )
