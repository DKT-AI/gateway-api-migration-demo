"""E2E tests: Gateway API routing (after migration).

Verifies that all routing works correctly through Gateway API.
Run after: kubectl apply -f manifests/04-gateway-api/
"""

import httpx


async def test_products_list(client: httpx.AsyncClient):
    resp = await client.get("/api/products")
    assert resp.status_code == 200
    products = resp.json()
    assert isinstance(products, list)
    assert len(products) == 5


async def test_product_detail(client: httpx.AsyncClient):
    resp = await client.get("/api/products/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Wireless Keyboard"


async def test_product_not_found(client: httpx.AsyncClient):
    resp = await client.get("/api/products/999")
    assert resp.status_code == 404


async def test_cart_operations(client: httpx.AsyncClient):
    """Cart should be reachable via cross-namespace routing."""
    # Get empty cart
    resp = await client.get("/api/cart/e2e-user")
    assert resp.status_code == 200
    assert resp.json()["items"] == []

    # Add item
    resp = await client.post(
        "/api/cart",
        json={
            "user_id": "e2e-user",
            "product_id": 1,
            "name": "Wireless Keyboard",
            "price": 49.99,
        },
    )
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


async def test_health(client: httpx.AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
