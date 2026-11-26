"""Fourteen more tools a shop might add over time, for the "too many tools" test only (they are never run).
Each one is well described. Two of them overlap with our four (order history, delivery estimate), as happens
in real projects once a tool list grows."""


def _tool(name: str, description: str, field: str, example: str) -> dict:
    return {"name": name, "description": description,
            "input_schema": {"type": "object",
                             "properties": {field: {"type": "string", "description": f"Like {example}"}},
                             "required": [field]}}


EXTRA_TOOLS = [
    _tool("get_order_history", "List every past order of a customer, with dates and totals. Use it when a customer "
          "asks what they bought before. Input: the customer ID, like C-101. Returns a list of orders.",
          "customer_id", "C-101"),
    _tool("estimate_delivery", "Estimate how many days a new order would take to reach a postcode. Use it before a "
          "customer buys. Input: the postcode, like 10115. Returns a number of days.", "postcode", "10115"),
    _tool("search_products", "Search Maple & Co.'s catalogue by keyword. Use it when a customer looks for a kind of "
          "product. Input: a search phrase, like rain jacket. Returns matching products and prices.", "query", "rain jacket"),
    _tool("get_product", "Get the details of one product by its product code. Input: the code, like P-220. Returns the "
          "name, price, sizes and colours.", "product_code", "P-220"),
    _tool("check_stock", "Check whether a product is in stock. Input: the product code, like P-220. Returns the number "
          "in stock.", "product_code", "P-220"),
    _tool("find_store", "Find the nearest Maple & Co. store. Input: a city, like Berlin. Returns the address and opening "
          "hours.", "city", "Berlin"),
    _tool("get_return_policy", "Get Maple & Co.'s return policy for a product category. Input: the category, like tents. "
          "Returns the return window and conditions.", "category", "tents"),
    _tool("create_return_label", "Create a prepaid return label for an order the customer wants to send back. Input: "
          "the order number, like A1003. Returns a label link.", "order_id", "A1003"),
    _tool("update_address", "Change the delivery address of an order that has not shipped yet. Input: the order "
          "number, like A1002. Returns the new address.", "order_id", "A1002"),
    _tool("cancel_order", "Cancel an order that has not shipped yet. Input: the order number, like A1002. Returns the "
          "cancellation status.", "order_id", "A1002"),
    _tool("apply_discount", "Apply a discount code to an order that has not shipped yet. Input: the code, like "
          "SPRING10. Returns the new total.", "code", "SPRING10"),
    _tool("get_loyalty_points", "Get a customer's loyalty points balance. Input: the customer ID, like C-101. Returns "
          "the points.", "customer_id", "C-101"),
    _tool("get_warranty", "Get the warranty terms for a product. Input: the product code, like P-220. Returns the "
          "warranty length and what it covers.", "product_code", "P-220"),
    _tool("book_repair", "Book a repair for a damaged product under warranty. Input: the order number, like A1001. "
          "Returns a repair booking number.", "order_id", "A1001"),
]
