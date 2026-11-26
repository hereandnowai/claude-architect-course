"""tool_choice: four ways to steer the model's choice. Claude's API enforces it (needs an API key).
Ollama accepts the field but ignores it, as this run shows: the small model still decides by itself."""
import sys

import anthropic

from maple_data import SYSTEM_PROMPT
from maple_tools import TOOLS

client = anthropic.Anthropic(base_url="http://localhost:11434", api_key="ollama")
MODEL = "qwen3.5:4b"

CHOICES = {
    "auto": {"type": "auto"},                       # the default: the model decides, a tool or plain text
    "any": {"type": "any"},                         # it must call a tool, but it picks which one
    "tool": {"type": "tool", "name": "get_order"},  # it must call this one tool
    "none": {"type": "none"},                       # it must not call any tool
}


def try_choice(question: str, choice: str) -> None:
    response = client.messages.create(
        model=MODEL, max_tokens=1024, system=SYSTEM_PROMPT, tools=TOOLS,
        messages=[{"role": "user", "content": question}],
        tool_choice=CHOICES[choice],
        thinking={"type": "disabled"},  # Ollama only
    )
    first = next((b.name for b in response.content if b.type == "tool_use"), "no tool")
    print(f"tool_choice {choice:<4} -> stop_reason: {response.stop_reason:<8}  first tool: {first}")


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What does Maple & Co. sell?"
    print(f"Question: {question}")
    for choice in CHOICES:
        try_choice(question, choice)
