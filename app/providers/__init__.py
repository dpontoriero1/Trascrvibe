from .base import Segment, TranscriptResult, TranscriptionError, TranscriptionProvider
from .demo import DEMO_MARKER, DemoProvider

__all__ = [
    "Segment",
    "TranscriptResult",
    "TranscriptionError",
    "TranscriptionProvider",
    "DemoProvider",
    "DEMO_MARKER",
    "build_provider",
]


def build_provider(settings) -> TranscriptionProvider:
    """Costruisce il provider configurato.

    'demo' restituisce sempre output marcato [DEMO] e non trascrive davvero;
    'faster-whisper' è il motore locale reale.
    """
    if settings.default_provider == "demo":
        return DemoProvider()
    from .faster_whisper_provider import FasterWhisperProvider

    return FasterWhisperProvider(
        model_size=settings.default_model,
        device=settings.device,
        compute_type=settings.compute_type,
    )
