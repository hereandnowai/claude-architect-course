"""The "before" picture: lazy tool descriptions, for our test only. Don't build real agents like this."""
from maple_tools import GET_ORDER_TOOL

# Episode 1's get_order (good, but with no boundary line) + episode 1's lazy get_shipment: the cliffhanger.
EP1_GET_ORDER_TOOL = {**GET_ORDER_TOOL, "description": (
    "Look up one Maple & Co. order by its order number. "
    "Use it whenever a customer asks about an order: where it is, what is in it, or when it arrives. "
    "Input: the order number, like A1001. "
    "Returns the customer's name, the items, the status and the arrival day, or an error.")}

LAZY_GET_SHIPMENT_TOOL = {"name": "get_shipment", "description": "Gets shipment info.",
                          "input_schema": {"type": "object", "properties": {"id": {"type": "string"}},
                                           "required": ["id"]}}

LAZY_TOOLS = [
    {"name": "get_order", "description": "Gets order info.",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
    LAZY_GET_SHIPMENT_TOOL,
    {"name": "find_customer", "description": "Finds customer.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "issue_refund", "description": "Issues refund.",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
                      "required": ["order_id", "amount"]}},
]

EP1_TOOLS = [EP1_GET_ORDER_TOOL, LAZY_GET_SHIPMENT_TOOL]
