"""Extra check (not a viewer step): does Claude also misroute with episode 1's lazy get_shipment?
Run from the project folder:  uv run extras/claude_lazy_check.py "When will PP-4821 arrive?"   (uses your Claude plan)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so we can import the project's files
import anyio
from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, tool

import agent_sdk
from lazy_tools import EP1_TOOLS
from maple_data import SYSTEM_PROMPT, get_order, get_shipment


def lazy_sdk_tool(definition: dict):
    @tool(definition["name"], definition["description"], definition["input_schema"])
    async def handler(args):
        if definition["name"] == "get_order":
            output = get_order(args["order_id"])
        else:
            output = get_shipment(args["id"])  # the lazy schema calls the field just "id"
        return {"content": [{"type": "text", "text": json.dumps(output)}]}
    return handler


lazy = create_sdk_mcp_server(name="maple", tools=[lazy_sdk_tool(t) for t in EP1_TOOLS])
agent_sdk.options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT, mcp_servers={"maple": lazy}, tools=[],
    allowed_tools=[f"mcp__maple__{t['name']}" for t in EP1_TOOLS], setting_sources=[], max_turns=10)

if __name__ == "__main__":
    anyio.run(agent_sdk.main, sys.argv[1] if len(sys.argv) > 1 else "When will PP-4821 arrive?")
