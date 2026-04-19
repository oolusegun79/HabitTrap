import json
from pathlib import Path


def load_state(week_folder: Path) -> dict:
    state_file = week_folder / "state.json"
    if not state_file.exists():
        return {}
    return json.loads(state_file.read_text(encoding="utf-8"))


def save_state(week_folder: Path, state: dict) -> None:
    state_file = week_folder / "state.json"
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


RESUMABLE = {"scripts_done", "image_gen_in_progress"}


def get_next_pending_script(state: dict) -> str | None:
    for i in range(1, 5):
        key = f"Script {i}"
        if state.get(key) in RESUMABLE:
            return key
    return None


def scripts_exist(state: dict) -> bool:
    return any(f"Script {i}" in state for i in range(1, 5))
