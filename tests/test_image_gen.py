import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.image_gen import generate_image, generate_images


def make_sdk_response(image_bytes_b64: str) -> MagicMock:
    mock_image = MagicMock()
    mock_image.image.image_bytes = image_bytes_b64
    mock_response = MagicMock()
    mock_response.generated_images = [mock_image]
    mock_client = MagicMock()
    mock_client.models.generate_images.return_value = mock_response
    return mock_client


def test_generate_image_saves_file(tmp_path):
    import base64
    raw = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    b64 = base64.b64encode(raw).decode()
    output_path = tmp_path / "image_001.png"

    with patch("modules.image_gen.genai.Client", return_value=make_sdk_response(b64)):
        generate_image("a prompt", "api_key", output_path)

    assert output_path.exists()
    assert output_path.read_bytes() == raw


def test_generate_images_skips_already_done(tmp_path):
    images_folder = tmp_path / "images"
    images_folder.mkdir()
    state = {"Script 1_images_done": ["image_001.png", "image_002.png"]}

    with patch("modules.image_gen.generate_image") as mock_gen:
        with patch("modules.image_gen.time.sleep"):
            generate_images(
                ["prompt 1", "prompt 2", "prompt 3"],
                "api_key",
                images_folder,
                state,
                "Script 1",
                lambda s: None,
            )
    assert mock_gen.call_count == 1


def test_generate_images_updates_state_after_each_image(tmp_path):
    images_folder = tmp_path / "images"
    images_folder.mkdir()
    state = {}
    save_calls = []

    with patch("modules.image_gen.generate_image"):
        with patch("modules.image_gen.time.sleep"):
            generate_images(
                ["prompt 1", "prompt 2"],
                "api_key",
                images_folder,
                state,
                "Script 1",
                lambda s: save_calls.append(dict(s)),
            )

    assert len(save_calls) == 2
    assert "image_001.png" in save_calls[0]["Script 1_images_done"]
    assert "image_002.png" in save_calls[1]["Script 1_images_done"]
