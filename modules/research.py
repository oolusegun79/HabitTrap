import json
import requests
import anthropic
from modules.skills import load_skill


def call_perplexity(system_prompt: str, user_message: str, api_key: str) -> str:
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def research_topics(api_key: str) -> list[str]:
    system_prompt = load_skill("topic-research")
    raw = call_perplexity(system_prompt, "Generate 4 topics now.", api_key)
    start = raw.find("{")
    end = raw.rfind("}") + 1
    data = json.loads(raw[start:end])
    return data["topics"]


def write_script(topic: str, api_key: str) -> str:
    system_prompt = load_skill("script-writer")
    return call_perplexity(
        system_prompt,
        f"Write a complete script for this topic: {topic}",
        api_key,
    )


def humanize_script(script: str, anthropic_api_key: str) -> str:
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    system_prompt = load_skill("grammar-humanizer")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": script}],
    )
    return message.content[0].text
