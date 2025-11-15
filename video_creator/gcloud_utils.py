"""Utility helpers that interact with Google Cloud services."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

# Optional imports so that unit tests can run without Google Cloud libraries.
try:  # pragma: no cover - import-time check
    from google.cloud import texttospeech  # type: ignore
    from google.cloud import aiplatform  # type: ignore
    from google.protobuf import json_format  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - graceful degradation
    texttospeech = None  # type: ignore
    aiplatform = None  # type: ignore
    json_format = None  # type: ignore
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from .config import NarrationScript, SlideSpec, VideoPlan


def generate_slide_narrations(slides: Iterable[SlideSpec]) -> NarrationScript:
    """Create a narration text for each slide.

    The implementation uses a simple heuristic, but it can be replaced with a call
    to a large language model (Vertex AI's Gemini) if desired.  The local
    implementation keeps the script deterministic for unit testing.
    """

    slide_text: List[str] = []
    for slide in slides:
        bullet_lines = " ".join(slide.bullet_points)
        slide_text.append(
            f"{slide.title}. {bullet_lines}. This project demonstrates my role in "
            f"{slide.title.lower()} by leveraging modern cloud architecture."
        )
    return NarrationScript(slide_text=slide_text)


def synthesize_narration(plan: VideoPlan, narration: NarrationScript) -> Path:
    """Use Google Cloud Text-to-Speech to synthesize the narration audio."""
    if texttospeech is None:  # pragma: no cover - error path
        raise RuntimeError(
            "google-cloud-texttospeech is not installed. Install dependencies from "
            "requirements.txt to synthesize narration."
        ) from _IMPORT_ERROR
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=narration.combined)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=plan.voice_name.split("-")[0], voice_name=plan.voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=plan.speaking_rate,
        pitch=plan.voice_pitch,
    )

    response = client.synthesize_speech(
        request=texttospeech.SynthesizeSpeechRequest(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )
    )

    audio_path = plan.output_dir / "audio" / "narration.mp3"
    audio_path.write_bytes(response.audio_content)
    return audio_path


def generate_image(prompt: str, destination: Path, project_id: str, location: str) -> Path:
    """Generate an illustrative image for a slide using Vertex AI Imagen."""
    if aiplatform is None or json_format is None:  # pragma: no cover - error path
        raise RuntimeError(
            "google-cloud-aiplatform is not installed. Install dependencies from "
            "requirements.txt to generate imagery."
        ) from _IMPORT_ERROR
    aiplatform.init(project=project_id, location=location)
    model = aiplatform.ImageGenerationModel.from_pretrained("imagen-2.0-fast")
    prediction = model.predict(prompt=prompt, negative_prompt="text artifacts")

    image = prediction.images[0]
    destination.write_bytes(image._image_bytes)
    metadata_path = destination.with_suffix(".json")
    metadata_path.write_text(json.dumps(json_format.MessageToDict(prediction._raw_prediction), indent=2))
    return destination


def generate_slide_images(plan: VideoPlan) -> List[Path]:
    """Generate an image for every slide in the plan."""
    image_paths: List[Path] = []
    for idx, slide in enumerate(plan.slides, start=1):
        destination = plan.output_dir / "images" / f"slide_{idx:02d}.png"
        image_paths.append(
            generate_image(
                prompt=slide.prompt,
                destination=destination,
                project_id=plan.project_id,
                location=plan.location,
            )
        )
    return image_paths
