"""
Quick live API test — generates one image and one video.
Run: uv run python test_live.py
Output: test_output/sample_image.png and test_output/sample_video.mp4
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from modules.image_gen import generate_image
from modules.video_gen import generate_video

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not set in .env")

OUTPUT_DIR = Path(__file__).parent / "test_output"
OUTPUT_DIR.mkdir(exist_ok=True)

PROMPT = (
    "Cartoon illustration, white background, bald cartoon child with round white head "
    "wearing yellow ribbed turtleneck sweater, small X marks on cheeks, sitting at a desk "
    "staring at a glowing phone screen with a confused expression. "
    "Clean line art, simple flat colors, thin black outlines."
)

print("Generating image with Imagen 4...")
image_path = OUTPUT_DIR / "sample_image.png"
generate_image(PROMPT, GEMINI_API_KEY, image_path)
print(f"  Saved: {image_path}  ({image_path.stat().st_size:,} bytes)")

print("\nGenerating video with Veo 2 (this takes ~2-3 min, polling every 10s)...")
video_path = OUTPUT_DIR / "sample_video.mp4"
generate_video(PROMPT, GEMINI_API_KEY, video_path)
print(f"  Saved: {video_path}  ({video_path.stat().st_size:,} bytes)")

print("\nDone! Check test_output/ for the results.")
