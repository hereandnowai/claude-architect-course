"""Maple & Co., a made-up outdoor-gear shop: fake customers, orders and parcels, and what our code can do with them."""

CUSTOMERS = {
    "emma@example.com": {"customer_id": "C-101", "name": "Emma", "orders": ["A1001"]},
    "liam@example.com": {"customer_id": "C-102", "name": "Liam", "orders": ["A1002"]},
    "olivia@example.com": {"customer_id": "C-103", "name": "Olivia", "orders": ["A1003"]},
    "noah@example.com": {"customer_id": "C-104", "name": "Noah", "orders": ["A1004"]},
}

ORDERS = {
    "A1001": {"customer": "Emma", "items": ["Trail tent for two"], "price": 249.00,
              "status": "shipped", "arrives": "Friday", "tracking": "PP-4821"},
    "A1002": {"customer": "Liam", "items": ["Hiking boots", "Wool socks"], "price": 164.00,
              "status": "packing", "arrives": "Tuesday", "tracking": None},
    "A1003": {"customer": "Olivia", "items": ["Rain jacket"], "price": 89.00,
              "status": "delivered", "arrives": "already delivered", "tracking": "PP-3907"},
    "A1004": {"customer": "Noah", "items": ["Sleeping bag"], "price": 119.00,
              "status": "shipped", "arrives": "Monday", "tracking": "PP-5150"},
}

SHIPMENTS = {
    "PP-4821": {"carrier": "ParcelPost", "where": "Local depot", "arrives": "Friday"},
    "PP-3907": {"carrier": "ParcelPost", "where": "Delivered to the front door", "arrives": "already delivered"},
    "PP-5150": {"carrier": "ParcelPost", "where": "On the delivery van", "arrives": "Monday"},
}

REFUNDS = []  # refunds we "issued" in this run (a fake shop: no real money moves)


def get_order(order_id: str) -> dict:
    """Find one order by its number. Unknown number: return an error, never a guess."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"error": f"No order with number {order_id}"}
    return {"order_id": order_id, **order}


def get_shipment(tracking_number: str) -> dict:
    """Track one parcel by its tracking number."""
    shipment = SHIPMENTS.get(tracking_number.strip().upper())
    if shipment is None:
        return {"error": f"No parcel with tracking number {tracking_number}"}
    return {"tracking_number": tracking_number, **shipment}


def find_customer(email: str) -> dict:
    """Find a customer by email address."""
    customer = CUSTOMERS.get(email.strip().lower())
    if customer is None:
        return {"error": f"No customer with email {email}"}
    return customer


def issue_refund(order_id: str, amount: float, reason: str) -> dict:
    """Record a refund. Never more than the order cost."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"error": f"No order with number {order_id}"}
    if amount > order["price"]:
        return {"error": f"Refund of {amount} is more than the order cost ({order['price']})"}
    REFUNDS.append({"order_id": order_id, "amount": amount, "reason": reason})
    return {"refund_id": f"R-{len(REFUNDS)}", "order_id": order_id, "amount": amount, "status": "refund recorded"}


SYSTEM_PROMPT = (
    "You are the friendly support agent of Maple & Co., an outdoor-gear shop. "
    "Use your tools to look up facts. Never guess. Answer in one or two short sentences."
)
