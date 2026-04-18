import time
from pathlib import Path
from google import genai
from google.genai import types

MODEL = "gemini-3.1-flash-image-preview"


def generate_image(prompt: str, api_key: str, output_path: Path) -> None:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )
    for part in response.parts:
        if part.inline_data is not None:
            part.as_image().save(str(output_path))
            return
    raise RuntimeError("Image generation returned no image data")


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
