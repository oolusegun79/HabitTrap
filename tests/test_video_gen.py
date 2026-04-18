import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.video_gen import generate_video, generate_videos


def make_submit_response(job_id: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": job_id}
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def make_poll_response(status: str, video_url: str = "") -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": status, "video_url": video_url}
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def make_download_response(content: bytes) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.content = content
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_generate_video_saves_file_on_success(tmp_path):
    output_path = tmp_path / "video_001.mp4"
    video_bytes = b"fake_video_data"

    with patch("modules.video_gen.requests.post", return_value=make_submit_response("job_123")):
        with patch("modules.video_gen.requests.get") as mock_get:
            with patch("modules.video_gen.time.sleep"):
                mock_get.side_effect = [
                    make_poll_response("processing"),
                    make_poll_response("completed", "https://example.com/video.mp4"),
                    make_download_response(video_bytes),
                ]
                generate_video("a prompt", "api_key", output_path)

    assert output_path.exists()
    assert output_path.read_bytes() == video_bytes


def test_generate_video_raises_on_failure(tmp_path):
    output_path = tmp_path / "video_001.mp4"
    with patch("modules.video_gen.requests.post", return_value=make_submit_response("job_abc")):
        with patch("modules.video_gen.requests.get", return_value=make_poll_response("failed")):
            with patch("modules.video_gen.time.sleep"):
                with pytest.raises(RuntimeError, match="Video generation failed"):
                    generate_video("a prompt", "api_key", output_path)


def test_generate_videos_skips_completed(tmp_path):
    videos_folder = tmp_path / "videos"
    videos_folder.mkdir()
    state = {"Script 1_videos_done": ["video_001.mp4"]}

    with patch("modules.video_gen.generate_video") as mock_gen:
        generate_videos(
            ["prompt 1", "prompt 2"],
            "api_key",
            videos_folder,
            state,
            "Script 1",
            lambda s: None,
        )
    assert mock_gen.call_count == 1


def test_generate_videos_updates_state_after_each_video(tmp_path):
    videos_folder = tmp_path / "videos"
    videos_folder.mkdir()
    state = {}
    save_calls = []

    with patch("modules.video_gen.generate_video"):
        generate_videos(
            ["prompt 1", "prompt 2"],
            "api_key",
            videos_folder,
            state,
            "Script 1",
            lambda s: save_calls.append(dict(s)),
        )

    assert len(save_calls) == 2
    assert "video_001.mp4" in save_calls[0]["Script 1_videos_done"]
    assert "video_002.mp4" in save_calls[1]["Script 1_videos_done"]
