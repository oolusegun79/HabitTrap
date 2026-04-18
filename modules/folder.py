from pathlib import Path
from datetime import datetime


def get_week_folder(base_dir: Path) -> Path:
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
