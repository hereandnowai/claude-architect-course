"""Teaser for episode 2: add a second tool with a lazy description. Does the agent still pick the right one?
Run from the project folder:  uv run teaser/lazy_tool.py lazy "Where is my order A1001?"
Variants: lazy (good get_order + lazy get_shipment), both-lazy, both-good."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so we can import maple_data
import anthropic

from maple_data import GET_ORDER_TOOL, SYSTEM_PROMPT, get_order

client = anthropic.Anthropic(base_url="http://localhost:11434", api_key="ollama")
MODEL = "qwen3.5:4b"

SHIPMENTS = {"PP-4821": {"carrier": "ParcelPost", "where": "Local depot", "arrives": "Friday"}}


def get_shipment(tracking_number: str) -> dict:
    shipment = SHIPMENTS.get(tracking_number.strip().upper())
    return shipment or {"error": f"No shipment with tracking number {tracking_number}"}


LAZY_SHIPMENT_TOOL = {"name": "get_shipment", "description": "Gets shipment info.",
                      "input_schema": {"type": "object", "properties": {"id": {"type": "string"}},
                                       "required": ["id"]}}
LAZY_ORDER_TOOL = {"name": "get_order", "description": "Gets order info.",
                   "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}},
                                    "required": ["order_id"]}}
GOOD_SHIPMENT_TOOL = {
    "name": "get_shipment",
    "description": ("Track a parcel with the carrier, by its tracking number. "
                    "Use it only when you already have a tracking number, like PP-4821. "
                    "It does not accept order numbers like A1001: for those, use get_order. "
                    "Returns the carrier, where the parcel is now and the arrival day, or an error."),
    "input_schema": {"type": "object", "properties": {"id": {"type": "string",
                     "description": "The tracking number, like PP-4821"}}, "required": ["id"]}}

VARIANTS = {"lazy": [GET_ORDER_TOOL, LAZY_SHIPMENT_TOOL],
            "both-lazy": [LAZY_ORDER_TOOL, LAZY_SHIPMENT_TOOL],
            "both-good": [GET_ORDER_TOOL, GOOD_SHIPMENT_TOOL]}


def run_tool(name: str, tool_input: dict) -> dict:
    if name == "get_order":
        return get_order(tool_input["order_id"])
    if name == "get_shipment":
        return get_shipment(tool_input["id"])
    return {"error": f"Unknown tool: {name}"}


def ask(question: str, tools: list) -> str:
    messages = [{"role": "user", "content": question}]
    for turn in range(10):
        start = time.time()
        response = client.messages.create(model=MODEL, max_tokens=1024, system=SYSTEM_PROMPT,
                                          tools=tools, messages=messages,
                                          thinking={"type": "disabled"})  # Ollama only
        print(f"turn {turn}: {response.stop_reason} ({time.time() - start:.1f} s)")
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason != "tool_use":
            return f"Stopped early: {response.stop_reason}"
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  tool_use: {block.name} {block.input}")
                output = run_tool(block.name, block.input)
                print(f"  tool_result: {json.dumps(output)}")
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(output)})
        messages.append({"role": "user", "content": results})
    return "Stopped by the safety net."


if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "lazy"
    question = sys.argv[2] if len(sys.argv) > 2 else "Where is my order A1001?"
    print(f"[variant: {variant}]")
    print("Answer:", ask(question, VARIANTS[variant]))
