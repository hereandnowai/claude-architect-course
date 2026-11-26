"""The same agent with the Claude Agent SDK. The brain: Claude, on your Claude plan."""
import json
import sys
from typing import Annotated

import anyio
from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock,
                              ToolResultBlock, ToolUseBlock, UserMessage,
                              create_sdk_mcp_server, query, tool)

from maple_data import GET_ORDER_DESCRIPTION, SYSTEM_PROMPT, get_order


@tool("get_order", GET_ORDER_DESCRIPTION,
      {"order_id": Annotated[str, "The order number, like A1001"]})
async def get_order_tool(args):
    order = get_order(args["order_id"])
    return {"content": [{"type": "text", "text": json.dumps(order)}]}


maple = create_sdk_mcp_server(name="maple", tools=[get_order_tool])

options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"maple": maple},
    tools=[],                                 # no built-in tools: no files, no shell
    allowed_tools=["mcp__maple__get_order"],  # our tool may run without asking
    setting_sources=[],                       # ignore settings files: a clean agent
    max_turns=10,                             # a safety net, like in our own loop
)


async def main(question: str) -> None:
    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Claude asks for a tool: {block.name} {block.input}")
                elif isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, UserMessage) and isinstance(message.content, list):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    print(f"Our tool answered: {block.content}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}, {message.num_turns} turns, "
                  f"{message.duration_ms / 1000:.1f} s")


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "Where is my order A1001?"
    anyio.run(main, question)
