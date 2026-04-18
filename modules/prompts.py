import anthropic
from pathlib import Path
from modules.skills import load_skill


def call_claude(system_prompt: str, user_message: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def generate_image_prompts(script: str, api_key: str) -> str:
    system_prompt = load_skill("image-prompt-generator")
    return call_claude(
        system_prompt,
        f"Generate image prompts for this script:\n\n{script}",
        api_key,
    )


def generate_video_prompts(script: str, image_prompts: str, api_key: str) -> str:
    system_prompt = load_skill("video-prompt-generator")
    user_msg = f"Script:\n{script}\n\nImage prompts:\n{image_prompts}"
    return call_claude(system_prompt, user_msg, api_key)


def generate_thumbnail(topic: str, script: str, api_key: str) -> str:
    system_prompt = load_skill("thumbnail-generator")
    return call_claude(
        system_prompt,
        f"Topic: {topic}\n\nScript (first 500 chars): {script[:500]}",
        api_key,
    )


def write_prompt_files(
    script_folder: Path,
    topic: str,
    script: str,
    api_key: str,
    script_num: int,
) -> None:
    image_prompts = generate_image_prompts(script, api_key)
    video_prompts = generate_video_prompts(script, image_prompts, api_key)
    thumbnail = generate_thumbnail(topic, script, api_key)

    (script_folder / f"Script{script_num}ImagePrompt.md").write_text(image_prompts, encoding="utf-8")
    (script_folder / "ScriptVideoPrompt.md").write_text(video_prompts, encoding="utf-8")
    (script_folder / "Thumbnail.md").write_text(thumbnail, encoding="utf-8")
