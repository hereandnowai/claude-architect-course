"""Maple's four tools as an MCP server. Any MCP client can use them: Claude Code, the Agent SDK, and more."""
import json
import os
import re
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError
from mcp.types import CallToolResult, TextContent

import maple_data as shop
from maple_tools import FIND_CUSTOMER_TOOL, GET_ORDER_TOOL, GET_SHIPMENT_TOOL, ISSUE_REFUND_TOOL

mcp = MCPServer("maple")
API_KEY = os.environ.get("MAPLE_API_KEY", "")  # comes from .mcp.json, never written in a file
POLICIES = Path(__file__).parent / "policies"
TRIES = {}  # how often each parcel was tracked: our pretend carrier times out on the first try for PP-5150


def ok(data: dict) -> CallToolResult:
    """A normal answer. "Nothing found" is a normal answer too, not an error."""
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(data))])


def fail(category: str, retryable: bool, message: str) -> CallToolResult:
    """A structured error: isError says the call failed; the category and isRetryable say what to do next."""
    error = {"errorCategory": category, "isRetryable": retryable, "message": message}
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(error))], is_error=True)


@mcp.tool(description=GET_ORDER_TOOL["description"])
def get_order(order_id: str) -> CallToolResult:
    if not re.fullmatch(r"A\d{4}", order_id.strip().upper()):
        return fail("validation", False, f"{order_id} is not an order number. Order numbers look like A1001. "
                    "Tracking numbers like PP-4821 go to get_shipment.")
    order = shop.get_order(order_id)
    return ok({"order_id": order_id, "found": False} if "error" in order else order)


@mcp.tool(description=GET_SHIPMENT_TOOL["description"])
def get_shipment(tracking_number: str) -> CallToolResult:
    number = tracking_number.strip().upper()
    if not re.fullmatch(r"PP-\d{4}", number):
        return fail("validation", False, f"{tracking_number} is not a tracking number. Tracking numbers look like "
                    "PP-4821. Order numbers like A1001 go to get_order.")
    TRIES[number] = TRIES.get(number, 0) + 1
    if number == "PP-5150" and TRIES[number] == 1:  # pretend the carrier's system is slow, once
        return fail("transient", True, "The carrier's tracking system timed out. Please try again.")
    parcel = shop.get_shipment(number)
    return ok({"tracking_number": number, "found": False} if "error" in parcel else parcel)


@mcp.tool(description=FIND_CUSTOMER_TOOL["description"])
def find_customer(email: str) -> CallToolResult:
    customer = shop.find_customer(email)
    return ok({"email": email, "found": False} if "error" in customer else customer)


@mcp.tool(description=ISSUE_REFUND_TOOL["description"])
def issue_refund(order_id: str, amount: float, reason: str) -> CallToolResult:
    if not API_KEY or API_KEY.startswith("${"):  # missing, or not filled in
        return fail("permission", False, "The refund system needs MAPLE_API_KEY. A human must fix the setup.")
    order = shop.get_order(order_id)
    if "error" in order:
        return fail("validation", False, f"There is no order {order_id}, so there is nothing to refund.")
    if amount > order["price"]:
        return fail("business", False, f"A refund can't be more than the order's price (${order['price']:.2f}). "
                    f"Tell the customer we can refund up to ${order['price']:.2f}.")
    return ok(shop.issue_refund(order_id, amount, reason))


@mcp.resource("maple://policies", description="A catalogue of Maple's policy files: one line about each.")
def policy_catalogue() -> str:
    return "\n".join(f"maple://policies/{p.stem}: {p.read_text().splitlines()[2][2:]}"
                     for p in sorted(POLICIES.glob("*.md")))


@mcp.resource("maple://policies/{name}", description="One Maple policy file, like maple://policies/returns.")
def policy(name: str) -> str:
    if name not in [p.stem for p in POLICIES.glob("*.md")]:
        raise ResourceNotFoundError(f"There is no policy called {name}.")
    return (POLICIES / f"{name}.md").read_text()


if __name__ == "__main__":
    mcp.run()  # stdio: the client starts this file, and they talk through stdin and stdout
