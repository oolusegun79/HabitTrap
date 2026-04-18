import os
from pathlib import Path
from dotenv import load_dotenv
from modules.folder import create_week_structure, get_week_folder
from modules.state import load_state, save_state, get_next_pending_script, scripts_exist
from modules.research import research_topics, write_script, humanize_script
from modules.prompts import write_prompt_files
from modules.voiceover import generate_voiceover
from modules.image_gen import generate_images
from modules.video_gen import generate_videos

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
        stripped = line.strip()
        if not stripped:
            continue
        is_new = stripped.startswith("Image ") or stripped.startswith("Video ")
        if is_new and current_lines:
            prompts.append(" ".join(current_lines).strip())
            current_lines = [stripped]
        elif is_new:
            current_lines = [stripped]
        else:
            current_lines.append(stripped)
    if current_lines:
        prompts.append(" ".join(current_lines).strip())
    return prompts


def process_media(week_folder: Path, script_key: str, state: dict) -> None:
    script_num = script_key.split(" ")[1]
    script_folder = week_folder / script_key

    image_prompts = parse_prompts(script_folder / f"Script{script_num}ImagePrompt.md")[:40]
    video_prompts = parse_prompts(script_folder / "ScriptVideoPrompt.md")[:15]

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

    print(f"  Generating {len(video_prompts)} videos for {script_key}...")
    state[script_key] = "video_gen_in_progress"
    save_state(week_folder, state)
    generate_videos(
        video_prompts,
        get_env("GEMINI_API_KEY"),
        script_folder / "videos",
        state,
        script_key,
        lambda s: save_state(week_folder, s),
    )

    state[script_key] = "complete"
    save_state(week_folder, state)
    print(f"  {script_key} complete.")


def main() -> None:
    week_folder = get_week_folder(BASE_DIR)

    if not week_folder.exists():
        week_folder = create_week_structure(BASE_DIR)
        print(f"Created week folder: {week_folder.name}")

    state = load_state(week_folder)

    if not scripts_exist(state):
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

            write_prompt_files(script_folder, topic, clean_script, get_env("ANTHROPIC_API_KEY"), i)

            generate_voiceover(
                clean_script,
                get_env("ELEVENLABS_VOICE_ID"),
                get_env("ELEVENLABS_API_KEY"),
                script_folder / f"Script{i}.mp3",
            )

            state[script_key] = "scripts_done"
            save_state(week_folder, state)
            print(f"  {script_key} scripts + prompts + voiceover done.")

        print("\nProcessing images and videos for Script 1 (Friday)...")
        process_media(week_folder, "Script 1", state)

    else:
        next_script = get_next_pending_script(state)
        if next_script:
            print(f"Resuming: generating images and videos for {next_script}...")
            process_media(week_folder, next_script, state)
        else:
            print("All 4 scripts complete for this week. Nothing to do.")


if __name__ == "__main__":
    main()
