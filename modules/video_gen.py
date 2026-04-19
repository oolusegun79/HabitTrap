import re
import time
from pathlib import Path
from google import genai
from google.genai import types

MODEL = "veo-3.1-lite-generate-preview"


def _extract_image_num(prompt: str) -> int | None:
    # Matches "from Image 4" or "from Image 12" in the prompt header
    match = re.search(r"from Image (\d+)", prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None


def generate_video(
    prompt: str,
    api_key: str,
    output_path: Path,
    images_folder: Path | None = None,
) -> None:
    client = genai.Client(api_key=api_key)

    image = None
    if images_folder:
        img_num = _extract_image_num(prompt)
        if img_num is not None:
            img_path = images_folder / f"image_{img_num:03d}.png"
            if img_path.exists():
                image = types.Image(
                    image_bytes=img_path.read_bytes(),
                    mime_type="image/png",
                )

    if image is not None:
        operation = client.models.generate_videos(
            model=MODEL,
            image=image,
            prompt=prompt,
            config=types.GenerateVideosConfig(aspect_ratio="16:9"),
        )
    else:
        operation = client.models.generate_videos(
            model=MODEL,
            prompt=prompt,
            config=types.GenerateVideosConfig(aspect_ratio="16:9"),
        )

    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)

    if not operation.response.generated_videos:
        raise RuntimeError("Video generation returned no videos")

    generated_video = operation.response.generated_videos[0]
    client.files.download(file=generated_video.video)
    generated_video.video.save(str(output_path))


def generate_videos(
    prompts: list[str],
    api_key: str,
    videos_folder: Path,
    state: dict,
    script_key: str,
    save_state_fn,
    images_folder: Path | None = None,
) -> None:
    completed = state.get(f"{script_key}_videos_done", [])

    for i, prompt in enumerate(prompts, 1):
        filename = f"video_{i:03d}.mp4"
        if filename in completed:
            continue

        generate_video(prompt, api_key, videos_folder / filename, images_folder)
        completed.append(filename)
        state[f"{script_key}_videos_done"] = completed
        save_state_fn(state)
