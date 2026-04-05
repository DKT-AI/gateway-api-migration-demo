"""E2E tests: NGINX Ingress routing (before migration).

Verifies that routing works correctly through NGINX Ingress controller.
Run after: kubectl apply -f manifests/02-ingress-nginx/
"""

import httpx


async def test_products_list(client: httpx.AsyncClient):
    resp = await client.get("/api/products")
    assert resp.status_code == 200
    products = resp.json()
    assert isinstance(products, list)
    assert len(products) > 0


async def test_product_detail(client: httpx.AsyncClient):
    resp = await client.get("/api/products/1")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


async def test_product_not_found(client: httpx.AsyncClient):
    resp = await client.get("/api/products/999")
    assert resp.status_code == 404


async def test_health(client: httpx.AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
