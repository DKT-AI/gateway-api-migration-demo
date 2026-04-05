from typing import TypedDict


class Product(TypedDict):
    id: int
    name: str
    price: float
    category: str


class Recommendation(TypedDict):
    id: int
    name: str
    price: float
    reason: str


PRODUCTS: list[Product] = [
    {"id": 1, "name": "Wireless Keyboard", "price": 49.99, "category": "electronics"},
    {"id": 2, "name": "USB-C Hub", "price": 29.99, "category": "electronics"},
    {"id": 3, "name": "Laptop Stand", "price": 39.99, "category": "accessories"},
    {"id": 4, "name": "Mechanical Keyboard", "price": 89.99, "category": "electronics"},
    {"id": 5, "name": "Monitor Light Bar", "price": 59.99, "category": "accessories"},
]

RECOMMENDATIONS: dict[int, list[Recommendation]] = {
    1: [
        {
            "id": 3,
            "name": "Laptop Stand",
            "price": 39.99,
            "reason": "Often bought together",
        },
        {
            "id": 5,
            "name": "Monitor Light Bar",
            "price": 59.99,
            "reason": "Customers also liked",
        },
    ],
    2: [
        {"id": 1, "name": "Wireless Keyboard", "price": 49.99, "reason": "Great combo"},
        {
            "id": 3,
            "name": "Laptop Stand",
            "price": 39.99,
            "reason": "Often bought together",
        },
    ],
    3: [
        {
            "id": 5,
            "name": "Monitor Light Bar",
            "price": 59.99,
            "reason": "Complete your setup",
        },
    ],
    4: [
        {"id": 2, "name": "USB-C Hub", "price": 29.99, "reason": "Popular pairing"},
        {
            "id": 5,
            "name": "Monitor Light Bar",
            "price": 59.99,
            "reason": "Customers also liked",
        },
    ],
    5: [
        {
            "id": 3,
            "name": "Laptop Stand",
            "price": 39.99,
            "reason": "Often bought together",
        },
    ],
}


def get_all_products() -> list[Product]:
    return PRODUCTS


def get_product_by_id(product_id: int) -> Product | None:
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


def get_recommendations(product_id: int) -> list[Recommendation]:
    return RECOMMENDATIONS.get(product_id, [])
