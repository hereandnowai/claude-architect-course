"""A second agent, for Maple's staff: it works with the shop's policy files using Claude's built-in tools.
It gets only the four tools its job needs: Glob, Grep, Read and Edit. No shell, no new files, no Maple tools."""
import sys
from pathlib import Path

import anyio
from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock,
                              ToolResultBlock, ToolUseBlock, UserMessage, query)

POLICIES = Path(__file__).resolve().parent / "policies"
HELPER_TOOLS = ["Glob", "Grep", "Read", "Edit"]

options = ClaudeAgentOptions(
    system_prompt=("You help Maple & Co.'s staff with the shop's policy files in this folder. "
                   "Find facts in the files and quote them exactly. Keep every edit small."),
    cwd=str(POLICIES),            # the agent works inside the policies folder
    tools=HELPER_TOOLS,           # these built-in tools only: no Bash, no Write
    allowed_tools=HELPER_TOOLS,   # and they may run without asking
    setting_sources=[],           # ignore settings files: a clean agent
    max_turns=10,                 # a safety net
)


async def main(request: str) -> None:
    async for message in query(prompt=request, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Claude uses {block.name}: {block.input}")
                elif isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, UserMessage) and isinstance(message.content, list):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    text = " ".join(str(block.content).split())
                    print(f"  result{' (error)' if block.is_error else ''}: {text[:110]}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}, {message.num_turns} turns, {message.duration_ms / 1000:.1f} s")


if __name__ == "__main__":
    request = sys.argv[1] if len(sys.argv) > 1 else "Which file says how long the warranty on tents is?"
    anyio.run(main, request)
