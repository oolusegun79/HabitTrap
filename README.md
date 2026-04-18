# HabitTrap — Weekly YouTube Content Pipeline

Automated content pipeline for the [HabitTrap](https://www.youtube.com/@habit_trap) YouTube channel. Every Friday, run one command to research 4 psychology topics, write full scripts, generate voiceovers, image prompts, video prompts, and thumbnails — then generate images and videos staggered across 4 days to stay within API limits.

---

## What It Does

**Friday** — Run `python run.py` once:
- Picks 4 engaging psychology/behavior topics via Perplexity
- Writes a full teleprompter-ready script for each topic
- Grammar-corrects and humanizes each script via Claude
- Generates image prompts (40), video prompts (20), and a thumbnail prompt per script
- Generates a WAV voiceover per script via ElevenLabs
- Generates all 40 images + 20 videos for **Script 1**

**Saturday** — Run again → generates images + videos for **Script 2**

**Sunday** → **Script 3** | **Monday** → **Script 4**

At the end of the week, copy the video files from each `Script N/videos/` folder into CapCut, edit, and post.

---

## Setup

### 1. Install dependencies

```bash
uv venv .venv
uv pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and fill in all 5 keys:

```env
PERPLEXITY_API_KEY=
ANTHROPIC_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
GEMINI_API_KEY=
```

Get your Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey). Veo 3.1 video generation requires a paid Gemini API tier.

### 3. Test your API keys

Before the first full Friday run, generate one sample image and video to verify everything works:

```bash
uv run python test_live.py
```

Output is saved to `test_output/` (gitignored).

---

## Running

```bash
uv run python run.py
```

The script detects what day it is in the pipeline automatically — no flags needed.

---

## Output Structure

```
Apr 18 2026/
├── state.json
├── Script 1/
│   ├── Script1.md              ← teleprompter script
│   ├── Script1ImagePrompt.md   ← 40 image prompts
│   ├── ScriptVideoPrompt.md    ← 20 video prompts
│   ├── Thumbnail.md            ← thumbnail prompt + text
│   ├── Script1.wav             ← voiceover audio
│   ├── images/                 ← 40 generated PNGs
│   └── videos/                 ← 20 generated MP4s
├── Script 2/ ...
├── Script 3/ ...
└── Script 4/ ...
```

---

## Script Structure

Every script follows this format (~8–10 min):

1. **Hook** — grabs attention in the first 15 seconds
2. **Curiosity Bridge** — deepens the intrigue
3. **Stakes** — why this matters
4. **Main Body** — psychological story behind the behavior
5. **Twist** — counterintuitive insight that reframes everything
6. **Close** — emotional resolution
7. **CTA** — like, subscribe, comment

---

## Resuming After a Failure

If the pipeline crashes mid-run (e.g., at image 23 of 40), re-running `python run.py` resumes from where it left off. Each image and video filename is saved to `state.json` immediately after generation.

---

## Customizing Prompts

All AI prompt templates are in `.claude/skills/`:

| Skill | Controls |
|-------|----------|
| `topic-research` | How topics are selected |
| `script-writer` | Script structure and tone |
| `grammar-humanizer` | How scripts are edited |
| `image-prompt-generator` | Image prompt style and character rules |
| `video-prompt-generator` | Video prompt selection and style |
| `thumbnail-generator` | Thumbnail composition and text |

Edit the `SKILL.md` file in any skill folder to change how that stage behaves — no Python changes needed.

---

## APIs Used

| Stage | API | Model |
|-------|-----|-------|
| Topic research + scripts | Perplexity | `llama-3.1-sonar-large-128k-online` |
| Script humanization + prompts | Anthropic Claude | `claude-sonnet-4-6` |
| Voiceover | ElevenLabs | Your chosen voice ID |
| Image generation | Google Gemini | `gemini-3.1-flash-image-preview` |
| Video generation | Google Veo | `veo-3.1-lite-generate-preview` |

To upgrade video quality, change `MODEL` in `modules/video_gen.py` to `veo-3.1-fast-generate-preview` ($0.10/sec) or `veo-3.1-generate-preview` ($0.40/sec).

---

## Channel

**Niche:** Psychology of everyday human behavior — *"Why You Do That (Explained)"*

**Character:** Bald cartoon child in a yellow ribbed turtleneck sweater — appears in every image and video.
