import wave
import requests
from pathlib import Path


def generate_voiceover(
    text: str,
    voice_id: str,
    api_key: str,
    output_path: Path,
) -> None:
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=pcm_44100",
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

    pcm_data = response.content
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        wav_file.writeframes(pcm_data)
