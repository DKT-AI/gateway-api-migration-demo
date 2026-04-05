from typing import TypedDict


class Product(TypedDict):
    id: int
    name: str
    price: float
    category: str


PRODUCTS: list[Product] = [
    {"id": 1, "name": "Wireless Keyboard", "price": 49.99, "category": "electronics"},
    {"id": 2, "name": "USB-C Hub", "price": 29.99, "category": "electronics"},
    {"id": 3, "name": "Laptop Stand", "price": 39.99, "category": "accessories"},
    {"id": 4, "name": "Mechanical Keyboard", "price": 89.99, "category": "electronics"},
    {"id": 5, "name": "Monitor Light Bar", "price": 59.99, "category": "accessories"},
]


def get_all_products() -> list[Product]:
    return PRODUCTS


def get_product_by_id(product_id: int) -> Product | None:
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None
