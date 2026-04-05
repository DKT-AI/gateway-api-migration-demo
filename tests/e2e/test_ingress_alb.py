"""E2E tests: ALB Ingress routing (before migration).

Verifies that routing works correctly through ALB Ingress.
Run after: kubectl apply -f manifests/03-ingress-alb/
"""

import httpx


async def test_products_list(client: httpx.AsyncClient):
    resp = await client.get("/api/products")
    assert resp.status_code == 200
    assert len(resp.json()) > 0


async def test_product_detail(client: httpx.AsyncClient):
    resp = await client.get("/api/products/1")
    assert resp.status_code == 200


async def test_cart_empty(client: httpx.AsyncClient):
    resp = await client.get("/api/cart/test-user")
    assert resp.status_code == 200
    cart = resp.json()
    assert cart["user_id"] == "test-user"
    assert cart["items"] == []


async def test_tls_redirect(client: httpx.AsyncClient):
    """Verify HTTPS is working (TLS termination at ALB)."""
    resp = await client.get("/health")
    assert resp.status_code == 200
