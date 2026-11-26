"""Maple & Co., a made-up outdoor-gear shop: three fake orders and the get_order tool."""

ORDERS = {
    "A1001": {"customer": "Emma", "items": ["Trail tent for two"],
              "status": "shipped", "arrives": "Friday"},
    "A1002": {"customer": "Liam", "items": ["Hiking boots", "Wool socks"],
              "status": "packing", "arrives": "Tuesday"},
    "A1003": {"customer": "Olivia", "items": ["Rain jacket"],
              "status": "delivered", "arrives": "already delivered"},
}


def get_order(order_id: str) -> dict:
    """Find one order by its number. Unknown number: return an error, never a guess."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"error": f"No order with number {order_id}"}
    return {"order_id": order_id, **order}


SYSTEM_PROMPT = (
    "You are the friendly support agent of Maple & Co., an outdoor-gear shop. "
    "Use your tools to look up facts. Never guess. Answer in one or two short sentences."
)

GET_ORDER_DESCRIPTION = (
    "Look up one Maple & Co. order by its order number. "
    "Use it whenever a customer asks about an order: where it is, what is in it, or when it arrives. "
    "Input: the order number, like A1001. "
    "Returns the customer's name, the items, the status and the arrival day, or an error."
)

GET_ORDER_TOOL = {
    "name": "get_order",
    "description": GET_ORDER_DESCRIPTION,
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "The order number, like A1001"},
        },
        "required": ["order_id"],
    },
}
