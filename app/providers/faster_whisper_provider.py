from __future__ import annotations

from pathlib import Path

from .base import Segment, TranscriptResult, TranscriptionError, TranscriptionProvider


class FasterWhisperProvider(TranscriptionProvider):
    """Motore reale locale basato su faster-whisper (CTranslate2)."""

    name = "faster-whisper"
    is_demo = False
    supports_language_detection = True

    # Ottimizzazioni per modello:
    # - tiny/base: beam_size=1 (ricerca greedy) e nessun contesto dal segmento
    #   precedente: massima velocita', ideali per bozze e note brevi.
    # - small/medium/large-v3: beam_size=5: esplora 5 ipotesi per segmento,
    #   massima qualita' per interviste, lezioni e registrazioni importanti.
    # - vad_filter=True per tutti: salta i silenzi, meno lavoro inutile.
    _MODEL_OPTIONS = {
        "tiny": {"beam_size": 1, "condition_on_previous_text": False},
        "base": {"beam_size": 1, "condition_on_previous_text": False},
        "small": {"beam_size": 5},
        "medium": {"beam_size": 5},
        "large-v3": {"beam_size": 5},
    }

    def __init__(self, model_size: str = "base", device: str = "auto", compute_type: str = "auto"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _resolve_compute_type(self) -> str:
        """auto = float16 su GPU NVIDIA, int8 su CPU (molto piu' veloce del float32)."""
        if self.compute_type != "auto":
            return self.compute_type
        try:
            import ctranslate2

            if ctranslate2.get_cuda_device_count() > 0:
                return "float16"
        except Exception:
            pass
        return "int8"

    def _load_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise TranscriptionError(
                    "faster-whisper non è installato: esegui 'pip install -r requirements.txt'."
                ) from exc
            kwargs = {
                "compute_type": self._resolve_compute_type(),
            }
            if self.device != "auto":
                kwargs["device"] = self.device
            try:
                self._model = WhisperModel(self.model_size, **kwargs)
            except Exception as exc:
                raise TranscriptionError(
                    f"Impossibile caricare il modello '{self.model_size}': {type(exc).__name__}: {exc}"
                ) from exc
        return self._model

    def transcribe(
        self,
        media_path: Path,
        language: str | None = None,
        model_size: str | None = None,
    ) -> TranscriptResult:
        model = self._load_model()
        chosen_size = model_size or self.model_size
        options = dict(self._MODEL_OPTIONS.get(chosen_size, {"beam_size": 5}))
        try:
            try:
                # Percorso veloce: elaborazione a lotti (batching).
                from faster_whisper import BatchedInferencePipeline

                pipeline = BatchedInferencePipeline(model=model)
                segments_iter, info = pipeline.transcribe(
                    str(media_path),
                    language=language,
                    vad_filter=True,
                    batch_size=8,
                    beam_size=options.get("beam_size", 5),
                )
            except Exception:
                # Ripiego sicuro: metodo classico, un segmento alla volta.
                segments_iter, info = model.transcribe(
                    str(media_path), language=language, vad_filter=True, **options
                )
            segments = []
            for seg in segments_iter:
                text = (seg.text or "").strip()
                if text:
                    segments.append(
                        Segment(start=float(seg.start), end=float(seg.end), text=text)
                    )
        except TranscriptionError:
            raise
        except Exception as exc:
            raise TranscriptionError(
                f"Trascrizione fallita: {type(exc).__name__}: {exc}"
            ) from exc

        detected = getattr(info, "language", None) or language or "unknown"
        return TranscriptResult(
            segments=tuple(segments),
            language=detected,
            provider_name=self.name,
            is_demo=False,
        )
