import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.image_gen import generate_image, generate_images


def make_sdk_response(has_image: bool = True) -> MagicMock:
    part = MagicMock()
    if has_image:
        part.inline_data = MagicMock()
        part.as_image.return_value = MagicMock()
    else:
        part.inline_data = None
    mock_response = MagicMock()
    mock_response.parts = [part]
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    return mock_client


def test_generate_image_saves_file(tmp_path):
    output_path = tmp_path / "image_001.png"
    client = make_sdk_response(has_image=True)

    with patch("modules.image_gen.genai.Client", return_value=client):
        generate_image("a prompt", "api_key", output_path)

    client.models.generate_content.assert_called_once()
    client.models.generate_content.return_value.parts[0].as_image.return_value.save.assert_called_once_with(str(output_path))


def test_generate_image_raises_when_no_image_returned(tmp_path):
    output_path = tmp_path / "image_001.png"
    client = make_sdk_response(has_image=False)

    with patch("modules.image_gen.genai.Client", return_value=client):
        with pytest.raises(RuntimeError, match="no image data"):
            generate_image("a prompt", "api_key", output_path)


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
