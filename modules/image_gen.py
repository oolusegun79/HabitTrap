import time
import requests
from pathlib import Path

# Verify this URL against Nano Banana Pro API docs before production use
NANO_BANANA_URL = "https://api.nanobananapro.com/v1/generate"


def generate_image(prompt: str, api_key: str, output_path: Path) -> None:
    response = requests.post(
        NANO_BANANA_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"prompt": prompt, "width": 1024, "height": 1024},
    )
    response.raise_for_status()
    image_url = response.json()["url"]

    img_response = requests.get(image_url)
    img_response.raise_for_status()
    output_path.write_bytes(img_response.content)


def generate_images(
    prompts: list[str],
    api_key: str,
    images_folder: Path,
    state: dict,
    script_key: str,
    save_state_fn,
) -> None:
    completed = state.get(f"{script_key}_images_done", [])

    for i, prompt in enumerate(prompts, 1):
        filename = f"image_{i:03d}.png"
        if filename in completed:
            continue

        generate_image(prompt, api_key, images_folder / filename)
        completed.append(filename)
        state[f"{script_key}_images_done"] = completed
        save_state_fn(state)
        time.sleep(0.5)
