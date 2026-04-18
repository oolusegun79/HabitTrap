import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from modules.video_gen import generate_video, generate_videos


def make_operation(done: bool, has_videos: bool = False) -> MagicMock:
    op = MagicMock()
    op.done = done
    if has_videos:
        video = MagicMock()
        video.save = MagicMock()
        op.response.generated_videos = [MagicMock(video=video)]
    else:
        op.response.generated_videos = []
    return op


def make_sdk_client(operations: list) -> MagicMock:
    client = MagicMock()
    client.models.generate_videos.return_value = operations[0]
    client.operations.get.side_effect = operations[1:]
    return client


def test_generate_video_saves_file_on_success(tmp_path):
    output_path = tmp_path / "video_001.mp4"
    pending = make_operation(done=False)
    done_op = make_operation(done=True, has_videos=True)
    client = make_sdk_client([pending, pending, done_op])

    with patch("modules.video_gen.genai.Client", return_value=client):
        with patch("modules.video_gen.time.sleep"):
            generate_video("a prompt", "api_key", output_path)

    client.files.download.assert_called_once()
    done_op.response.generated_videos[0].video.save.assert_called_once_with(str(output_path))


def test_generate_video_raises_when_no_videos_returned(tmp_path):
    output_path = tmp_path / "video_001.mp4"
    done_op = make_operation(done=True, has_videos=False)
    client = make_sdk_client([done_op])

    with patch("modules.video_gen.genai.Client", return_value=client):
        with patch("modules.video_gen.time.sleep"):
            with pytest.raises(RuntimeError, match="no videos"):
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
