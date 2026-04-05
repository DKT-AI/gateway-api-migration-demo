"""E2E tests: Header-based routing (x-version: v2 → products-v2).

Verifies that HTTPRoute header matching correctly routes to v2.
Run after: kubectl apply -f manifests/04-gateway-api/
"""

import httpx


async def test_header_routes_to_v2(client: httpx.AsyncClient):
    """Request with x-version: v2 header should reach products-v2."""
    resp = await client.get(
        "/api/products",
        headers={"x-version": "v2"},
    )
    assert resp.status_code == 200
    products = resp.json()
    assert len(products) > 0


async def test_v2_has_recommendations(client: httpx.AsyncClient):
    """Products-v2 has the /recommendations endpoint."""
    resp = await client.get(
        "/api/products/1/recommendations",
        headers={"x-version": "v2"},
    )
    assert resp.status_code == 200
    recs = resp.json()
    assert isinstance(recs, list)
    assert len(recs) > 0
    assert "reason" in recs[0]


async def test_without_header_default_routing(client: httpx.AsyncClient):
    """Without x-version header, traffic goes to default (v1 or split)."""
    resp = await client.get("/api/products")
    assert resp.status_code == 200


async def test_recommendations_accessible_via_v2_header(client: httpx.AsyncClient):
    """Recommendations endpoint is only on v2, reachable via header routing."""
    resp = await client.get(
        "/api/products/1/recommendations",
        headers={"x-version": "v2"},
    )
    assert resp.status_code == 200
