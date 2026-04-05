from typing import Any

import structlog
from fastapi import FastAPI
from pydantic import BaseModel

from cart.config import settings
from cart.data import add_to_cart, get_cart

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
)

log: structlog.stdlib.BoundLogger = structlog.get_logger()

app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
)


class AddItemRequest(BaseModel):
    user_id: str
    product_id: int
    name: str
    price: float
    quantity: int = 1


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.service_name}


@app.post("/api/cart")
async def add_item(request: AddItemRequest) -> dict[str, Any]:
    cart_data = add_to_cart(
        user_id=request.user_id,
        item={
            "product_id": request.product_id,
            "name": request.name,
            "price": request.price,
            "quantity": request.quantity,
        },
    )
    log.info(
        "item_added_to_cart",
        user_id=request.user_id,
        product_id=request.product_id,
    )
    return cart_data  # type: ignore[return-value]


@app.get("/api/cart/{user_id}")
async def get_user_cart(user_id: str) -> dict[str, Any]:
    cart_data = get_cart(user_id)
    log.info("getting_cart", user_id=user_id, item_count=len(cart_data["items"]))
    return cart_data  # type: ignore[return-value]
