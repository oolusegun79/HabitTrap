import os
from pathlib import Path
from dotenv import load_dotenv
from modules.folder import create_week_structure, get_week_folder
from modules.state import load_state, save_state, get_next_pending_script, scripts_exist
from modules.research import research_topics, write_script, humanize_script
from modules.prompts import write_prompt_files
from modules.voiceover import generate_voiceover
from modules.image_gen import generate_images

load_dotenv()
BASE_DIR = Path(__file__).parent


def get_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Missing required env var: {key}")
    return value


def parse_prompts(prompt_file: Path) -> list[str]:
    lines = prompt_file.read_text(encoding="utf-8").splitlines()
    prompts = []
    current_lines: list[str] = []
    for line in lines:
        stripped = line.strip().lstrip("*").strip()
        if not stripped or stripped.startswith("---"):
            continue
        is_new = stripped.startswith("Image ") or stripped.startswith("Video ")
        if is_new and current_lines:
            if current_lines[0].startswith("Image ") or current_lines[0].startswith("Video "):
                prompts.append(" ".join(current_lines).strip())
            current_lines = [stripped]
        elif is_new:
            current_lines = [stripped]
        else:
            current_lines.append(stripped)
    if current_lines and (current_lines[0].startswith("Image ") or current_lines[0].startswith("Video ")):
        prompts.append(" ".join(current_lines).strip())
    return prompts


def process_media(week_folder: Path, script_key: str, state: dict) -> None:
    script_num = script_key.split(" ")[1]
    script_folder = week_folder / script_key

    image_prompts = parse_prompts(script_folder / f"Script{script_num}ImagePrompt.md")[:40]

    print(f"  Generating {len(image_prompts)} images for {script_key}...")
    state[script_key] = "image_gen_in_progress"
    save_state(week_folder, state)
    generate_images(
        image_prompts,
        get_env("GEMINI_API_KEY"),
        script_folder / "images",
        state,
        script_key,
        lambda s: save_state(week_folder, s),
    )

    state[script_key] = "complete"
    save_state(week_folder, state)
    print(f"  {script_key} complete.")


APPROVAL_FILE = "approved.txt"


def write_initial_scripts(week_folder: Path, state: dict) -> None:
    print("Friday run: researching topics and writing all 4 scripts...")
    topics = research_topics(get_env("PERPLEXITY_API_KEY"))
    print(f"Topics selected: {topics}")

    for i, topic in enumerate(topics, 1):
        script_key = f"Script {i}"
        script_folder = week_folder / script_key
        print(f"\nWriting {script_key}: {topic}")

        raw_script = write_script(topic, get_env("PERPLEXITY_API_KEY"))
        clean_script = humanize_script(raw_script, get_env("ANTHROPIC_API_KEY"))

        script_file = script_folder / f"Script{i}.md"
        script_file.write_text(f"# {topic}\n\n{clean_script}", encoding="utf-8")

        state[script_key] = "awaiting_approval"
        state[f"{script_key}_topic"] = topic
        save_state(week_folder, state)
        print(f"  {script_key} written.")


def parse_script_file(script_file: Path) -> str:
    content = script_file.read_text(encoding="utf-8")
    lines = content.splitlines()
    if lines and lines[0].lstrip().startswith("#"):
        return "\n".join(lines[1:]).lstrip()
    return content


def process_after_approval(week_folder: Path, state: dict) -> None:
    awaiting = [f"Script {i}" for i in range(1, 5) if state.get(f"Script {i}") == "awaiting_approval"]
    print(f"Approval found. Generating prompts + voiceovers for {len(awaiting)} script(s)...")

    for script_key in awaiting:
        i = int(script_key.split(" ")[1])
        script_folder = week_folder / script_key
        topic = state.get(f"{script_key}_topic", "")
        body = parse_script_file(script_folder / f"Script{i}.md")
        mp3_file = script_folder / f"Script{i}.mp3"
        thumb_file = script_folder / "Thumbnail.md"

        print(f"\n{script_key}:")
        if not thumb_file.exists():
            print(f"  Generating prompts...")
            write_prompt_files(script_folder, topic, body, get_env("ANTHROPIC_API_KEY"), i)
        else:
            print(f"  Prompts already exist, skipping.")

        if not mp3_file.exists():
            print(f"  Generating voiceover...")
            generate_voiceover(
                body,
                get_env("ELEVENLABS_VOICE_ID"),
                get_env("ELEVENLABS_API_KEY"),
                mp3_file,
            )
        else:
            print(f"  Voiceover already exists, skipping.")

        state[script_key] = "scripts_done"
        save_state(week_folder, state)
        print(f"  {script_key} done.")


def main() -> None:
    week_folder = get_week_folder(BASE_DIR)

    if not week_folder.exists():
        week_folder = create_week_structure(BASE_DIR)
        print(f"Created week folder: {week_folder.name}")

    state = load_state(week_folder)

    if not scripts_exist(state):
        write_initial_scripts(week_folder, state)
        print(
            f"\n>>> Scripts written. Review them in '{week_folder}/' and create "
            f"'{APPROVAL_FILE}' in that folder, then re-run to continue. <<<"
        )
        return

    awaiting = [f"Script {i}" for i in range(1, 5) if state.get(f"Script {i}") == "awaiting_approval"]
    if awaiting:
        if not (week_folder / APPROVAL_FILE).exists():
            print(f"Scripts awaiting approval: {awaiting}")
            print(f"Review them and create '{week_folder}/{APPROVAL_FILE}' to continue.")
            return
        process_after_approval(week_folder, state)
        print("\nProcessing images for Script 1 (Friday)...")
        process_media(week_folder, "Script 1", state)
        return

    next_script = get_next_pending_script(state)
    if next_script:
        print(f"Resuming: generating images for {next_script}...")
        process_media(week_folder, next_script, state)
    else:
        print("All 4 scripts complete for this week. Nothing to do.")


if __name__ == "__main__":
    main()
