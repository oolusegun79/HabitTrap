import time
import requests
from pathlib import Path

# Verify these URLs against Flow API docs before production use
FLOW_SUBMIT_URL = "https://api.flow.ai/v1/generate"
FLOW_POLL_URL = "https://api.flow.ai/v1/jobs/{job_id}"


def generate_video(prompt: str, api_key: str, output_path: Path) -> None:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        FLOW_SUBMIT_URL,
        headers=headers,
        json={"prompt": prompt, "duration": 3, "aspect_ratio": "16:9"},
    )
    response.raise_for_status()
    job_id = response.json()["id"]

    for _ in range(60):
        time.sleep(5)
        poll = requests.get(
            FLOW_POLL_URL.format(job_id=job_id),
            headers=headers,
        )
        poll.raise_for_status()
        result = poll.json()

        if result["status"] == "completed":
            video_response = requests.get(result["video_url"])
            video_response.raise_for_status()
            output_path.write_bytes(video_response.content)
            return
        elif result["status"] == "failed":
            raise RuntimeError(f"Video generation failed for job {job_id}: {result.get('error')}")

    raise TimeoutError(f"Video generation timed out for job {job_id}")


def generate_videos(
    prompts: list[str],
    api_key: str,
    videos_folder: Path,
    state: dict,
    script_key: str,
    save_state_fn,
) -> None:
    completed = state.get(f"{script_key}_videos_done", [])

    for i, prompt in enumerate(prompts, 1):
        filename = f"video_{i:03d}.mp4"
        if filename in completed:
            continue

        generate_video(prompt, api_key, videos_folder / filename)
        completed.append(filename)
        state[f"{script_key}_videos_done"] = completed
        save_state_fn(state)
