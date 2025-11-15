"""Builds the final video using generated media assets."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from moviepy.editor import AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip
from moviepy.editor import TextClip, concatenate_videoclips

from .config import SlideSpec, VideoPlan


FONT = "DejaVu-Sans"


def _build_slide_clip(image_path: Path, slide: SlideSpec, narration_start: float) -> CompositeVideoClip:
    """Create a composite clip for a single slide."""
    image_clip = ImageClip(str(image_path)).set_duration(slide.duration)
    title_clip = (
        TextClip(slide.title, fontsize=70, font=FONT, color="white", stroke_color="black", stroke_width=2)
        .set_position(("center", 80))
        .set_duration(slide.duration)
    )
    bullet_text = "\n".join(f"• {line}" for line in slide.bullet_points)
    bullets_clip = (
        TextClip(bullet_text, fontsize=40, font=FONT, color="white", method="caption", size=image_clip.size)
        .set_position((80, 200))
        .set_duration(slide.duration)
    )

    timestamp_clip = (
        TextClip(
            f"{narration_start:02.0f}s",
            fontsize=32,
            font=FONT,
            color="yellow",
            stroke_color="black",
            stroke_width=2,
        )
        .set_position((image_clip.w - 120, image_clip.h - 120))
        .set_duration(slide.duration)
    )

    return CompositeVideoClip([image_clip, title_clip, bullets_clip, timestamp_clip])


def build_video(plan: VideoPlan, image_paths: Sequence[Path], narration_path: Path) -> Path:
    """Assemble the narrated slides into a final MP4 video."""
    slide_clips = []
    current_time = 0.0
    for slide, image in zip(plan.slides, image_paths):
        clip = _build_slide_clip(image, slide, current_time)
        slide_clips.append(clip)
        current_time += slide.duration

    video = concatenate_videoclips(slide_clips, method="compose")
    narration_clip = AudioFileClip(str(narration_path))

    audio_clips: Iterable[AudioFileClip] = [narration_clip]
    if plan.background_music:
        music_clip = AudioFileClip(str(plan.background_music)).volumex(0.25)
        music_clip = music_clip.set_duration(video.duration)
        audio_clips = [CompositeAudioClip([narration_clip, music_clip])]

    video = video.set_audio(audio_clips[0])

    output_path = plan.output_dir / "video" / "expertise_showcase.mp4"
    video.write_videofile(
        str(output_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(plan.output_dir / "audio" / "temp_audio.m4a"),
    )
    return output_path
