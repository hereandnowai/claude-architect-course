"""The agent loop, written by hand. The brain: a free local model in Ollama."""
import json
import sys
import time

import anthropic

from maple_data import SYSTEM_PROMPT
from maple_tools import TOOLS, run_tool

client = anthropic.Anthropic(base_url="http://localhost:11434", api_key="ollama")
MODEL = "qwen3.5:4b"
MAX_TURNS = 10  # a safety net only: the loop really stops on end_turn


def ask(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    for turn in range(MAX_TURNS):
        start = time.time()
        response = client.messages.create(
            model=MODEL, max_tokens=1024, system=SYSTEM_PROMPT,
            tools=TOOLS, messages=messages,
            thinking={"type": "disabled"},  # Ollama only: faster on a laptop. Leave it out for Claude.
        )
        print(f"turn {turn}: {response.stop_reason} ({time.time() - start:.1f} s)")
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  tool_use: {block.name} {block.input}")
                    output = run_tool(block.name, block.input)
                    print(f"  tool_result: {json.dumps(output)}")
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": json.dumps(output)})
            messages.append({"role": "user", "content": results})
        else:
            return f"Stopped early: {response.stop_reason}"
    return "Stopped by the safety net: too many turns."


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "Where is my order A1001?"
    print("Answer:", ask(question))
