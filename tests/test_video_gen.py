import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from modules.video_gen import generate_video, generate_videos


def make_operation(done: bool, video_uri: str = "", error=None) -> MagicMock:
    op = MagicMock()
    op.done = done
    op.error = error
    if done and video_uri:
        op.result.generated_videos[0].video.uri = video_uri
    return op


def make_sdk_client(operations: list) -> MagicMock:
    client = MagicMock()
    client.models.generate_videos.return_value = operations[0]
    client.operations.get.side_effect = operations[1:]
    return client


def test_generate_video_saves_file_on_success(tmp_path):
    output_path = tmp_path / "video_001.mp4"
    video_bytes = b"fake_video_data"

    pending = make_operation(done=False)
    done_op = make_operation(done=True, video_uri="gs://bucket/video.mp4")
    client = make_sdk_client([pending, pending, done_op])

    mock_dl = MagicMock()
    mock_dl.content = video_bytes
    mock_dl.raise_for_status = MagicMock()

    with patch("modules.video_gen.genai.Client", return_value=client):
        with patch("modules.video_gen.requests.get", return_value=mock_dl):
            with patch("modules.video_gen.time.sleep"):
                generate_video("a prompt", "api_key", output_path)

    assert output_path.exists()
    assert output_path.read_bytes() == video_bytes


def test_generate_video_raises_on_error(tmp_path):
    output_path = tmp_path / "video_001.mp4"
    pending = make_operation(done=False)
    error_op = make_operation(done=False)
    error_op.error = "Something went wrong"
    client = make_sdk_client([pending, error_op])

    with patch("modules.video_gen.genai.Client", return_value=client):
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
