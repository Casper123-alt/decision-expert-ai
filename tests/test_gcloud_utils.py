from video_creator.config import SlideSpec
from video_creator.gcloud_utils import generate_slide_narrations


def test_generate_slide_narrations_creates_contextual_text():
    slides = [
        SlideSpec(
            title="Data Platform Leadership",
            bullet_points=["Built reliable pipelines", "Mentored engineers"],
            prompt="",
        ),
        SlideSpec(
            title="ML Operations",
            bullet_points=["Automated deployment", "Implemented monitoring"],
            prompt="",
        ),
    ]

    narration = generate_slide_narrations(slides)

    assert len(narration.slide_text) == 2
    assert "Data Platform Leadership" in narration.slide_text[0]
    assert "ML Operations" in narration.slide_text[1]
    assert narration.combined.count("This project demonstrates") == 2
