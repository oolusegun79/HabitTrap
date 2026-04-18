import time
import requests
from pathlib import Path
from google import genai
from google.genai import types


def generate_video(prompt: str, api_key: str, output_path: Path) -> None:
    client = genai.Client(api_key=api_key)
    operation = client.models.generate_videos(
        model="veo-3.0-generate-001",
        prompt=prompt,
        config=types.GenerateVideosConfig(aspect_ratio="16:9"),
    )

    for _ in range(60):
        time.sleep(10)
        operation = client.operations.get_videos_operation(operation=operation)
        if operation.done:
            video_uri = operation.response.generated_videos[0].video.uri
            download_url = video_uri.replace("gs://", "https://storage.googleapis.com/")
            resp = requests.get(download_url, headers={"x-goog-api-key": api_key})
            resp.raise_for_status()
            output_path.write_bytes(resp.content)
            return
        if hasattr(operation, "error") and operation.error:
            raise RuntimeError(f"Video generation failed: {operation.error}")

    raise TimeoutError(f"Video generation timed out after 600s")


def generate_videos(
    prompts: list[str],
    api_key: str,
    videos_folder: Path,
    state: dict,
    script_key: str,
    save_state_fn,
) -> None:
    completed = state.get(f"{script_key}_videos_done", [])

    for i, prompt in enumerate(prompts, 1):
        filename = f"video_{i:03d}.mp4"
        if filename in completed:
            continue

        generate_video(prompt, api_key, videos_folder / filename)
        completed.append(filename)
        state[f"{script_key}_videos_done"] = completed
        save_state_fn(state)
