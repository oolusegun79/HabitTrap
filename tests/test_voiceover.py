import wave
import struct
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.voiceover import generate_voiceover


def make_fake_pcm() -> bytes:
    return struct.pack("<" + "h" * 100, *([0] * 100))


def test_generate_voiceover_creates_wav_file(tmp_path):
    mock_resp = MagicMock()
    mock_resp.content = make_fake_pcm()
    mock_resp.raise_for_status = MagicMock()

    output_path = tmp_path / "test.wav"
    with patch("modules.voiceover.requests.post", return_value=mock_resp):
        generate_voiceover("Hello world", "voice_id_123", "api_key_123", output_path)

    assert output_path.exists()
    with wave.open(str(output_path), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 44100


def test_generate_voiceover_sends_correct_voice_id(tmp_path):
    mock_resp = MagicMock()
    mock_resp.content = make_fake_pcm()
    mock_resp.raise_for_status = MagicMock()

    output_path = tmp_path / "test.wav"
    with patch("modules.voiceover.requests.post", return_value=mock_resp) as mock_post:
        generate_voiceover("text", "voice_abc", "key_xyz", output_path)

    url = mock_post.call_args[0][0]
    assert "voice_abc" in url


def test_generate_voiceover_uses_correct_api_key(tmp_path):
    mock_resp = MagicMock()
    mock_resp.content = make_fake_pcm()
    mock_resp.raise_for_status = MagicMock()

    output_path = tmp_path / "test.wav"
    with patch("modules.voiceover.requests.post", return_value=mock_resp) as mock_post:
        generate_voiceover("text", "voice_id", "my_secret_key", output_path)

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["xi-api-key"] == "my_secret_key"
