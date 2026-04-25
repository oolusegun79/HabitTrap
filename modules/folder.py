import re
from pathlib import Path
from datetime import datetime
from modules.state import load_state

WEEK_PATTERN = re.compile(r"^[A-Z][a-z]{2} \d{2} \d{4}$")


def _is_week_complete(folder: Path) -> bool:
    state = load_state(folder)
    if not state:
        return False
    return all(state.get(f"Script {i}") == "complete" for i in range(1, 5))


def get_week_folder(base_dir: Path) -> Path:
    candidates = []
    for d in base_dir.iterdir():
        if d.is_dir() and WEEK_PATTERN.match(d.name):
            try:
                date = datetime.strptime(d.name, "%b %d %Y")
            except ValueError:
                continue
            if not _is_week_complete(d):
                candidates.append((date, d))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    name = datetime.now().strftime("%b %d %Y")
    return base_dir / name


def create_week_structure(base_dir: Path) -> Path:
    week_folder = get_week_folder(base_dir)
    week_folder.mkdir(exist_ok=True)
    for i in range(1, 5):
        script_folder = week_folder / f"Script {i}"
        script_folder.mkdir(exist_ok=True)
        (script_folder / "images").mkdir(exist_ok=True)
        (script_folder / "videos").mkdir(exist_ok=True)
    return week_folder
