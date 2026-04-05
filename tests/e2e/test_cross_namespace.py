"""E2E tests: Cross-namespace routing (cart in gatewaydemo-cart).

Verifies that HTTPRoute + ReferenceGrant enable cross-namespace routing.
Cart service lives in gatewaydemo-cart namespace but is routable via the
Gateway in gatewaydemo namespace.
Run after: kubectl apply -f manifests/04-gateway-api/
"""

import httpx


async def test_cart_reachable(client: httpx.AsyncClient):
    """Cart service should be reachable despite being in a different namespace."""
    resp = await client.get("/api/cart/cross-ns-test")
    assert resp.status_code == 200
    cart = resp.json()
    assert cart["user_id"] == "cross-ns-test"


async def test_cart_add_item(client: httpx.AsyncClient):
    """Adding items to cart should work through cross-namespace route."""
    resp = await client.post(
        "/api/cart",
        json={
            "user_id": "cross-ns-test",
            "product_id": 1,
            "name": "Wireless Keyboard",
            "price": 49.99,
            "quantity": 2,
        },
    )
    assert resp.status_code == 200
    cart = resp.json()
    assert cart["user_id"] == "cross-ns-test"
    assert len(cart["items"]) >= 1


async def test_cart_service_identifies_correctly(client: httpx.AsyncClient):
    """Health check confirms we're hitting the cart service."""
    # Note: /health on the cart path depends on routing configuration.
    # The main health endpoint may hit products service.
    # Cart is accessed via /api/cart/* path.
    resp = await client.get("/api/cart/health-check-user")
    assert resp.status_code == 200
    assert resp.json()["user_id"] == "health-check-user"
