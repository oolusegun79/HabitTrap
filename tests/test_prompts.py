import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.prompts import call_claude, generate_image_prompts, generate_video_prompts, generate_thumbnail, write_prompt_files


def make_claude_client(text: str) -> MagicMock:
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=text)]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_msg
    return mock_client


def test_call_claude_returns_text():
    mock_client = make_claude_client("claude output")
    with patch("modules.prompts.anthropic.Anthropic", return_value=mock_client):
        result = call_claude("system", "user", "fake_key")
    assert result == "claude output"


def test_generate_image_prompts_calls_claude():
    mock_client = make_claude_client("Image 1: prompt\nImage 2: prompt")
    with patch("modules.prompts.anthropic.Anthropic", return_value=mock_client):
        with patch("modules.prompts.load_skill", return_value="image skill"):
            result = generate_image_prompts("script text", "fake_key")
    assert "Image 1" in result


def test_write_prompt_files_creates_three_files(tmp_path):
    script_folder = tmp_path / "Script 1"
    script_folder.mkdir()

    with patch("modules.prompts.generate_image_prompts", return_value="image prompts"):
        with patch("modules.prompts.generate_video_prompts", return_value="video prompts"):
            with patch("modules.prompts.generate_thumbnail", return_value="thumbnail prompt"):
                write_prompt_files(script_folder, "Test topic", "script", "fake_key", 1)

    assert (script_folder / "Script1ImagePrompt.md").exists()
    assert (script_folder / "ScriptVideoPrompt.md").exists()
    assert (script_folder / "Thumbnail.md").exists()


def test_write_prompt_files_uses_correct_script_number(tmp_path):
    script_folder = tmp_path / "Script 3"
    script_folder.mkdir()

    with patch("modules.prompts.generate_image_prompts", return_value="img"):
        with patch("modules.prompts.generate_video_prompts", return_value="vid"):
            with patch("modules.prompts.generate_thumbnail", return_value="thumb"):
                write_prompt_files(script_folder, "topic", "script", "fake_key", 3)

    assert (script_folder / "Script3ImagePrompt.md").exists()
