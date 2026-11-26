"""Test tool choice: ask the same questions many times and count how often the model picks the right first tool.
Run:  uv run tool_test.py good 10      tool sets: ep1, lazy, good, many
Add "trap" for the keyword-trap system prompt, or q1 q4 ... to ask only those questions."""
import sys
import time
from collections import Counter

import anthropic

from extra_tools import EXTRA_TOOLS
from lazy_tools import EP1_TOOLS, LAZY_TOOLS
from maple_data import SYSTEM_PROMPT
from maple_tools import TOOLS

client = anthropic.Anthropic(base_url="http://localhost:11434", api_key="ollama")
MODEL = "qwen3.5:4b"

TOOL_SETS = {"ep1": EP1_TOOLS, "lazy": LAZY_TOOLS, "good": TOOLS, "many": TOOLS + EXTRA_TOOLS}
TRAP_PROMPT = SYSTEM_PROMPT + " Whenever the customer mentions an order, call get_order."

QUESTIONS = [  # (question, the right first tool; "none" = answer without a tool)
    ("When will PP-4821 arrive?", "get_shipment"),
    ("Where is my order A1001?", "get_order"),
    ("Hi, I'm Noah, noah@example.com. Which orders do I have?", "find_customer"),
    ("My parcel PP-5150 hasn't come yet. Where is it now?", "get_shipment"),
    ("What's in order A1002, and when does it arrive?", "get_order"),
    ("Order A1003 arrived torn. Please refund the 89 dollars.", "get_order"),
    ("What does Maple & Co. sell?", "none"),
    ("My order is on its way, and the tracking number is PP-4821. When will it arrive?", "get_shipment"),
]


def first_tool(question: str, tools: list, system: str) -> str:
    """Send the question once. Return the first tool the model asks for, or "none"."""
    response = client.messages.create(
        model=MODEL, max_tokens=1024, system=system, tools=tools,
        messages=[{"role": "user", "content": question}],
        thinking={"type": "disabled"},  # Ollama only
    )
    return next((b.name for b in response.content if b.type == "tool_use"), "none")


if __name__ == "__main__":
    tool_set = sys.argv[1] if len(sys.argv) > 1 else "good"
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    system = TRAP_PROMPT if "trap" in sys.argv else SYSTEM_PROMPT
    tools = TOOL_SETS[tool_set]
    only = [int(a[1:]) for a in sys.argv[3:] if a[:1] == "q" and a[1:].isdigit()]
    print(f"Tool set: {tool_set} ({len(tools)} tools), prompt: {'trap' if 'trap' in sys.argv else 'normal'}, "
          f"{runs} runs per question")
    start, total, asked = time.time(), 0, 0
    for number, (question, right) in enumerate(QUESTIONS, 1):
        if only and number not in only:
            continue
        asked += 1
        picks = Counter(first_tool(question, tools, system) for _ in range(runs))
        total += picks[right]
        print(f"Q{number} {picks[right]:>2}/{runs}  right: {right:<13} picked: {dict(picks)}  | {question}")
    print(f"Total: {total}/{runs * asked} right first tools ({time.time() - start:.0f} s)")
