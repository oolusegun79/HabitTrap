import pytest
from pathlib import Path
from modules.skills import load_skill

def test_load_skill_reads_correct_file():
    # The actual topic-research SKILL.md exists at .claude/skills/topic-research/SKILL.md
    result = load_skill("topic-research")
    assert isinstance(result, str)
    assert len(result) > 50  # should have real content

def test_load_skill_raises_for_missing_skill():
    with pytest.raises(FileNotFoundError):
        load_skill("nonexistent-skill-xyz")
