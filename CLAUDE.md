# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Python is managed via `uv`. Always prefix Python/pytest commands with `uv run`.

```bash
# Run all tests
uv run pytest tests/ -v

# Run a single test file
uv run pytest tests/test_state.py -v

# Run a single test by name
uv run pytest tests/test_research.py::test_research_topics_returns_list_of_four -v

# Run the pipeline
uv run python run.py

# Install dependencies
uv pip install -r requirements.txt
```

## Architecture

This is a weekly YouTube content pipeline for the HabitTrap channel (psychology of everyday behavior). Running `python run.py` every Friday auto-generates 4 video packages. Image/video generation is staggered across 4 days (Friday–Monday) to avoid API rate limits.

### Run logic (`run.py`)

`main()` branches on whether scripts already exist in `state.json`:
- **No scripts yet (Friday):** research 4 topics → write + humanize 4 scripts → generate prompts + voiceovers for all 4 → generate images + videos for Script 1 only
- **Scripts exist (Sat–Mon):** find first script with status `"scripts_done"` → generate its images + videos

### State machine

Each week folder contains `state.json` tracking per-script status:
```
pending → scripts_done → image_gen_in_progress → video_gen_in_progress → complete
```
Granular checkpointing keys (`"Script 1_images_done": ["image_001.png", ...]`) allow resuming mid-generation if an API call fails.

### Prompt templates (`.claude/skills/*/SKILL.md`)

All AI prompts live in skill files, not in Python code. Modules load them at runtime via `modules/skills.py:load_skill(name)`. To change how topics are researched, scripts are written, or images are prompted — edit the SKILL.md, not the module.

Six skills: `topic-research`, `script-writer`, `grammar-humanizer`, `image-prompt-generator`, `video-prompt-generator`, `thumbnail-generator`.

### API modules

| Module | API | Key env var |
|--------|-----|-------------|
| `research.py` | Perplexity (topics + scripts) | `PERPLEXITY_API_KEY` |
| `research.py` | Anthropic Claude (humanize) | `ANTHROPIC_API_KEY` |
| `prompts.py` | Anthropic Claude (prompt files) | `ANTHROPIC_API_KEY` |
| `voiceover.py` | ElevenLabs (WAV, PCM wrapped) | `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` |
| `image_gen.py` | Gemini 3.1 Flash Image (`generate_content` + Pillow) | `GEMINI_API_KEY` |
| `video_gen.py` | Veo 3.1 Lite (`veo-3.1-lite-generate-preview`, async operation+poll) | `GEMINI_API_KEY` |

### Live API testing

`test_live.py` generates one image and one video using real API keys. Run it to verify keys and check output quality before a full Friday run:

```bash
uv run python test_live.py
# Output saved to test_output/ (gitignored)
```

To swap video quality vs cost, change `MODEL` in `modules/video_gen.py`:
- `veo-3.1-lite-generate-preview` — $0.05/sec (~$0.40/video)
- `veo-3.1-fast-generate-preview` — $0.10/sec (~$0.80/video)
- `veo-3.1-generate-preview` — $0.40/sec (~$3.20/video)

### Output structure

Each run creates a dated folder (e.g., `Apr 18 2026/`) with `Script 1/` through `Script 4/`, each containing `Script{N}.md`, `Script{N}ImagePrompt.md`, `ScriptVideoPrompt.md`, `Thumbnail.md`, `Script{N}.wav`, `images/` (40 PNGs), `videos/` (20 MP4s).
