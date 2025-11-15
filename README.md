# Decision Expert AI - Google Cloud Video Creator

This repository contains a reference implementation that generates a narrated
"expertise showcase" video using Google Cloud services. It combines Vertex AI
Imagen for slide imagery, Cloud Text-to-Speech for narration, and MoviePy for
final video assembly.

## Features

- Declarative JSON configuration for the video structure.
- Automatic generation of supporting imagery per slide with Vertex AI Imagen.
- Narration synthesis with Google Cloud Text-to-Speech voices.
- Slide overlays containing titles, bullet points, and timestamps.
- Optional background music mixing.

## Prerequisites

1. Python 3.10 or newer.
2. A Google Cloud project with the following APIs enabled:
   - Vertex AI API
   - Cloud Text-to-Speech API
3. Service account credentials with permissions for the APIs above. Set the
   `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your JSON
   key file before running the script.
4. Install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

1. Create a configuration file following the structure in
   [`sample_plan.json`](./sample_plan.json). Customize the slide titles,
   bullet points, and prompts to reflect the expertise you want to highlight.

2. Run the generator:

   ```bash
   python create_expertise_video.py sample_plan.json
   ```

   The script will create the necessary directories inside the configured
   `output_dir` and produce the final video at
   `output_dir/video/expertise_showcase.mp4`.

3. (Optional) Provide a path to a background music file in your configuration to
   blend it with the synthesized narration.

## Customization Ideas

- Replace `generate_slide_narrations` in `video_creator/gcloud_utils.py` with a
  call to a Vertex AI Gemini model to dynamically author the narration.
- Adjust slide durations, fonts, or layout by modifying
  `video_creator/video_builder.py`.
- Use existing brand assets (logos, color palettes) by overriding the generated
  imagery before running the `build_video` step.

## Troubleshooting

- **Missing fonts**: `TextClip` relies on ImageMagick/FFmpeg and installed
  fonts. Install `fonts-dejavu` or update `FONT` in `video_builder.py`.
- **FFmpeg errors**: Ensure FFmpeg is installed and available on your `PATH`.
- **API errors**: Verify credentials and that billing is enabled for your
  project.
