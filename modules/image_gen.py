import base64
import time
from pathlib import Path
from google import genai
from google.genai import types


def generate_image(prompt: str, api_key: str, output_path: Path) -> None:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_images(
        model="imagen-4.0-fast-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1),
    )
    image_bytes = base64.b64decode(response.generated_images[0].image.image_bytes)
    output_path.write_bytes(image_bytes)


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
