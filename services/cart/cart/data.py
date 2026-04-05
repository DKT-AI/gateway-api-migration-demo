from typing import TypedDict


class CartItem(TypedDict):
    product_id: int
    name: str
    price: float
    quantity: int


class Cart(TypedDict):
    user_id: str
    items: list[CartItem]
    total: float


# In-memory cart store (no database — this is a networking demo)
_carts: dict[str, list[CartItem]] = {}


def get_cart(user_id: str) -> Cart:
    items = _carts.get(user_id, [])
    total = sum(item["price"] * item["quantity"] for item in items)
    return {"user_id": user_id, "items": items, "total": round(total, 2)}


def add_to_cart(user_id: str, item: CartItem) -> Cart:
    if user_id not in _carts:
        _carts[user_id] = []

    # Update quantity if product already in cart
    for existing in _carts[user_id]:
        if existing["product_id"] == item["product_id"]:
            existing["quantity"] += item["quantity"]
            return get_cart(user_id)

    _carts[user_id].append(item)
    return get_cart(user_id)


def clear_carts() -> None:
    """Reset all carts (for testing)."""
    _carts.clear()
