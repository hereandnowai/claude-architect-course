"""The Agent SDK with Maple's tools from our own MCP server: a separate process. The brain: Claude, on your Claude plan."""
import os
import sys

import anyio
from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage, SystemMessage, TextBlock,
                              ToolResultBlock, ToolUseBlock, UserMessage, query)

from maple_data import SYSTEM_PROMPT

MAPLE_SERVER = {"command": "uv", "args": ["run", "maple_server.py"],
                "env": {"MAPLE_API_KEY": os.environ.get("MAPLE_API_KEY", "")}}

options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"maple": MAPLE_SERVER},  # the same server Claude Code uses
    tools=["ListMcpResourcesTool", "ReadMcpResourceTool"],  # only these built-ins: they list and read resources
    allowed_tools=["mcp__maple__*", "ListMcpResourcesTool", "ReadMcpResourceTool"],  # may run without asking
    setting_sources=[],                   # ignore settings files: this agent is set up here, in code
    max_turns=10,                         # a safety net
)


async def main(question: str) -> None:
    async for message in query(prompt=question, options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print("MCP servers:", [(s["name"], s["status"]) for s in message.data.get("mcp_servers", [])])
        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Claude asks for a tool: {block.name} {block.input}")
                elif isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, UserMessage) and isinstance(message.content, list):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    error = " (isError)" if block.is_error else ""
                    print(f"Our server answered{error}: {block.content}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}, {message.num_turns} turns, {message.duration_ms / 1000:.1f} s")


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "Where is my order A1001?"
    anyio.run(main, question)
