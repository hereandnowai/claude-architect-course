"""Maple's four tools: what the model reads to decide which tool to call. One job each, clear boundaries."""
from maple_data import find_customer, get_order, get_shipment, issue_refund

GET_ORDER_TOOL = {
    "name": "get_order",
    "description": (
        "Look up one Maple & Co. order by its order number. "
        "Use it whenever a customer asks about an order: where it is, what is in it, or when it arrives. "
        "Input: the order number, like A1001. It does not accept tracking numbers like PP-4821: use get_shipment. "
        "Returns the customer's name, the items, the price, the status, the arrival day and the tracking number, "
        "or an error."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string", "description": "The order number, like A1001"}},
        "required": ["order_id"],
    },
}

GET_SHIPMENT_TOOL = {
    "name": "get_shipment",
    "description": (
        "Track a parcel with the carrier, by its tracking number. "
        "Use it when the customer gives a tracking number, like PP-4821, or after get_order returned one. "
        "It does not accept order numbers like A1001: for those, use get_order. "
        "Returns the carrier, where the parcel is now and the arrival day, or an error."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"tracking_number": {"type": "string", "description": "The tracking number, like PP-4821"}},
        "required": ["tracking_number"],
    },
}

FIND_CUSTOMER_TOOL = {
    "name": "find_customer",
    "description": (
        "Find a Maple & Co. customer by their email address. "
        "Use it when a customer gives their email and asks about their account or all of their orders. "
        "Input: the email address, like emma@example.com. It does not search by name or order number. "
        "Returns the customer ID, the name and a list of their order numbers, or an error."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"email": {"type": "string", "description": "The customer's email, like emma@example.com"}},
        "required": ["email"],
    },
}

ISSUE_REFUND_TOOL = {
    "name": "issue_refund",
    "description": (
        "Refund money for one order. This moves money, so only use it when the customer asks for a refund "
        "and you have already looked up the order with get_order in this conversation. "
        "Input: the order number, the amount in US dollars (never more than the order's price) and a short reason. "
        "Returns a refund ID and the status, or an error."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "The order number, like A1003"},
            "amount": {"type": "number", "description": "The amount in US dollars, like 89.00"},
            "reason": {"type": "string", "description": "A short reason, like: arrived torn"},
        },
        "required": ["order_id", "amount", "reason"],
    },
}

TOOLS = [GET_ORDER_TOOL, GET_SHIPMENT_TOOL, FIND_CUSTOMER_TOOL, ISSUE_REFUND_TOOL]


def run_tool(name: str, tool_input: dict) -> dict:
    """Run the tool the model asked for. Unknown tool: an error, never a guess."""
    if name == "get_order":
        return get_order(tool_input["order_id"])
    if name == "get_shipment":
        return get_shipment(tool_input["tracking_number"])
    if name == "find_customer":
        return find_customer(tool_input["email"])
    if name == "issue_refund":
        return issue_refund(tool_input["order_id"], tool_input["amount"], tool_input["reason"])
    return {"error": f"Unknown tool: {name}"}
