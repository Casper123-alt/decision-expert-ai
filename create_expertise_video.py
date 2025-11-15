"""CLI entry-point to generate an expertise showcase video using Google Cloud."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from video_creator.config import SlideSpec, VideoPlan
from video_creator.gcloud_utils import (
    generate_slide_images,
    generate_slide_narrations,
    synthesize_narration,
)
from video_creator.video_builder import build_video


def _load_plan(config_path: Path) -> VideoPlan:
    with config_path.open() as fp:
        raw = json.load(fp)

    slides = [
        SlideSpec(
            title=slide["title"],
            bullet_points=slide["bullet_points"],
            prompt=slide["prompt"],
            duration=slide.get("duration", 6.0),
        )
        for slide in raw["slides"]
    ]

    plan = VideoPlan(
        project_id=raw["project_id"],
        location=raw.get("location", "us-central1"),
        output_dir=Path(raw.get("output_dir", "artifacts")),
        voice_name=raw.get("voice_name", "en-US-Neural2-I"),
        speaking_rate=raw.get("speaking_rate", 1.02),
        voice_pitch=raw.get("voice_pitch", -1.5),
        background_music=Path(raw["background_music"]) if raw.get("background_music") else None,
        slides=slides,
    )
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "config",
        type=Path,
        help="Path to a JSON configuration file that defines the video plan.",
    )
    args = parser.parse_args()

    plan = _load_plan(args.config)
    plan.ensure_output_dirs()

    narration = generate_slide_narrations(plan.slides)
    narration_path = synthesize_narration(plan, narration)
    image_paths = generate_slide_images(plan)
    build_video(plan, image_paths, narration_path)


if __name__ == "__main__":
    main()
