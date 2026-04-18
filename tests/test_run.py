import pytest
import os
from pathlib import Path
from unittest.mock import patch
from run import parse_prompts, get_env


def test_parse_prompts_extracts_numbered_lines(tmp_path):
    prompt_file = tmp_path / "prompts.md"
    prompt_file.write_text(
        "Image 1: A cartoon child looking confused. White background.\n"
        "Image 2: A cartoon child pointing at a phone. White background.\n"
        "Image 3: A cartoon child sleeping at a desk. White background.\n"
    )
    result = parse_prompts(prompt_file)
    assert len(result) == 3
    assert result[0].startswith("Image 1:")


def test_parse_prompts_handles_multiline_prompt(tmp_path):
    prompt_file = tmp_path / "prompts.md"
    prompt_file.write_text(
        "Image 1: A cartoon child.\nLooking confused. White background.\n"
        "Image 2: Another scene.\n"
    )
    result = parse_prompts(prompt_file)
    assert len(result) == 2
    assert "Looking confused" in result[0]


def test_get_env_raises_for_missing_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(EnvironmentError, match="PERPLEXITY_API_KEY"):
            get_env("PERPLEXITY_API_KEY")


def test_get_env_returns_value_when_set():
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "abc123"}):
        assert get_env("PERPLEXITY_API_KEY") == "abc123"
