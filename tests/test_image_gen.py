import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.image_gen import generate_image, generate_images


def make_api_response(image_url: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"url": image_url}
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def make_image_bytes() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def test_generate_image_saves_file(tmp_path):
    output_path = tmp_path / "image_001.png"
    mock_gen = make_api_response("https://example.com/img.png")
    mock_download = MagicMock()
    mock_download.content = make_image_bytes()
    mock_download.raise_for_status = MagicMock()

    with patch("modules.image_gen.requests.post", return_value=mock_gen):
        with patch("modules.image_gen.requests.get", return_value=mock_download):
            generate_image("a prompt", "api_key", output_path)

    assert output_path.exists()
    assert output_path.read_bytes() == make_image_bytes()


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
