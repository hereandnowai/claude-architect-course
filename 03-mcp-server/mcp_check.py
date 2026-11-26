"""A tiny MCP client: it starts Maple's server, lists its tools and calls a few. No model, no AI: just the protocol."""
import os

import anyio
from mcp import Client, StdioServerParameters

SERVER = StdioServerParameters(command="uv", args=["run", "maple_server.py"],
                                env={"MAPLE_API_KEY": os.environ.get("MAPLE_API_KEY", "")})

CHECKS = [
    ("get_order", {"order_id": "A1001"}),
    ("get_shipment", {"tracking_number": "PP-4821"}),
    ("get_order", {"order_id": "PP-4821"}),                # the wrong kind of number
    ("get_order", {"order_id": "A1099"}),                  # no such order
    ("get_shipment", {"tracking_number": "PP-5150"}),      # the carrier times out...
    ("get_shipment", {"tracking_number": "PP-5150"}),      # ...so we try again
    ("issue_refund", {"order_id": "A1003", "amount": 120, "reason": "arrived torn"}),  # more than the price
]


async def main() -> None:
    async with Client(SERVER) as client:
        tools = await client.list_tools()
        print("Tools:", [tool.name for tool in tools.tools])
        for name, args in CHECKS:
            result = await client.call_tool(name, args)
            print(f"\n{name} {args}")
            print("  isError:", result.is_error)
            print("  text:", result.content[0].text)
        resources = await client.list_resources()
        print("\nResources:", [str(r.uri) for r in resources.resources])
        catalogue = await client.read_resource("maple://policies")
        print(catalogue.contents[0].text)


if __name__ == "__main__":
    anyio.run(main)
