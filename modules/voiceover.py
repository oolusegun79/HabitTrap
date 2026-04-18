import requests
from pathlib import Path


def generate_voiceover(
    text: str,
    voice_id: str,
    api_key: str,
    output_path: Path,
) -> None:
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        },
    )
    response.raise_for_status()
    output_path.write_bytes(response.content)
