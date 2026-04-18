import json
import pytest
from pathlib import Path
from modules.state import load_state, save_state, get_next_pending_script, scripts_exist

def test_load_state_returns_empty_dict_when_no_file(tmp_path):
    result = load_state(tmp_path)
    assert result == {}

def test_load_state_reads_existing_file(tmp_path):
    data = {"Script 1": "complete", "Script 2": "scripts_done"}
    (tmp_path / "state.json").write_text(json.dumps(data))
    result = load_state(tmp_path)
    assert result == data

def test_save_state_writes_json_file(tmp_path):
    data = {"Script 1": "complete"}
    save_state(tmp_path, data)
    written = json.loads((tmp_path / "state.json").read_text())
    assert written == data

def test_get_next_pending_script_returns_first_scripts_done():
    state = {
        "Script 1": "complete",
        "Script 2": "scripts_done",
        "Script 3": "scripts_done",
        "Script 4": "scripts_done",
    }
    assert get_next_pending_script(state) == "Script 2"

def test_get_next_pending_script_returns_none_when_all_complete():
    state = {
        "Script 1": "complete",
        "Script 2": "complete",
        "Script 3": "complete",
        "Script 4": "complete",
    }
    assert get_next_pending_script(state) is None

def test_scripts_exist_returns_false_when_empty():
    assert scripts_exist({}) is False

def test_scripts_exist_returns_true_when_scripts_present():
    assert scripts_exist({"Script 1": "scripts_done"}) is True
