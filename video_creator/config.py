"""Configuration models for the expertise video generator."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence


@dataclass
class SlideSpec:
    """Describes the content for a single slide in the video."""

    title: str
    bullet_points: Sequence[str]
    prompt: str
    duration: float = 6.0


@dataclass
class VideoPlan:
    """Configuration required to create an expertise showcase video."""

    project_id: str
    location: str
    output_dir: Path
    voice_name: str = "en-US-Neural2-I"
    speaking_rate: float = 1.02
    voice_pitch: float = -1.5
    background_music: Path | None = None
    slides: List[SlideSpec] = field(default_factory=list)

    def ensure_output_dirs(self) -> None:
        """Create the folders required to render the video if they do not exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "audio").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "video").mkdir(parents=True, exist_ok=True)


@dataclass
class NarrationScript:
    """Holds generated narration text for each slide."""

    slide_text: List[str]

    @property
    def combined(self) -> str:
        """Return the entire narration as a single paragraph."""
        return "\n\n".join(self.slide_text)
