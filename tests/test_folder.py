from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from modules.folder import create_week_structure, get_week_folder


def test_get_week_folder_returns_path_with_today(tmp_path):
    result = get_week_folder(tmp_path)
    # Just check it returns a Path with a date-like name (contains current year)
    assert result.parent == tmp_path
    assert "2026" in result.name  # adjust year if needed


def test_create_week_structure_creates_all_folders(tmp_path):
    week_folder = create_week_structure(tmp_path)
    assert week_folder.exists()
    for i in range(1, 5):
        script_folder = week_folder / f"Script {i}"
        assert script_folder.exists()
        assert (script_folder / "images").exists()
        assert (script_folder / "videos").exists()


def test_create_week_structure_is_idempotent(tmp_path):
    create_week_structure(tmp_path)
    week_folder = create_week_structure(tmp_path)
    assert week_folder.exists()
