from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class TranscriptResult:
    segments: tuple[Segment, ...]
    language: str
    provider_name: str
    is_demo: bool

    @property
    def full_text(self) -> str:
        return "\n".join(
            segment.text.strip() for segment in self.segments if segment.text.strip()
        )


class TranscriptionError(Exception):
    """Errore di trascrizione con messaggio mostrabile all'utente."""


class TranscriptionProvider(ABC):
    name: str = "abstract"
    is_demo: bool = False
    supports_language_detection: bool = True

    @abstractmethod
    def transcribe(
        self,
        media_path: Path,
        language: str | None = None,
        model_size: str | None = None,
    ) -> TranscriptResult:
        """Trascrive il file e restituisce segmenti temporizzati."""
        raise NotImplementedError
