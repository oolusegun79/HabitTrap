import pytest
from unittest.mock import patch, MagicMock
from modules.research import call_perplexity, research_topics, write_script, humanize_script


def make_perplexity_response(content: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_call_perplexity_returns_message_content():
    with patch("modules.research.requests.post") as mock_post:
        mock_post.return_value = make_perplexity_response("hello world")
        result = call_perplexity("system", "user", "fake_key")
    assert result == "hello world"


def test_call_perplexity_sends_correct_headers():
    with patch("modules.research.requests.post") as mock_post:
        mock_post.return_value = make_perplexity_response("ok")
        call_perplexity("system", "user", "my_key")
    call_args = mock_post.call_args
    assert call_args.kwargs["headers"]["Authorization"] == "Bearer my_key"


def test_research_topics_returns_list_of_four():
    topics_json = '{"topics": ["Topic A", "Topic B", "Topic C", "Topic D"]}'
    with patch("modules.research.requests.post") as mock_post:
        mock_post.return_value = make_perplexity_response(topics_json)
        with patch("modules.research.load_skill", return_value="system prompt"):
            result = research_topics("fake_key")
    assert len(result) == 4
    assert result[0] == "Topic A"


def test_write_script_returns_string():
    with patch("modules.research.requests.post") as mock_post:
        mock_post.return_value = make_perplexity_response("script content here")
        with patch("modules.research.load_skill", return_value="system prompt"):
            result = write_script("Why you do that", "fake_key")
    assert result == "script content here"


def test_humanize_script_calls_claude():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="humanized script")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    with patch("modules.research.anthropic.Anthropic", return_value=mock_client):
        with patch("modules.research.load_skill", return_value="humanizer prompt"):
            result = humanize_script("raw script", "fake_anthropic_key")
    assert result == "humanized script"
