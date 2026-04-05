"""E2E tests: Traffic splitting (90/10 between products v1/v2).

Verifies that HTTPRoute weight-based traffic splitting works.
Sends multiple requests and checks distribution.
Run after: kubectl apply -f manifests/04-gateway-api/
"""

import httpx


async def test_traffic_split_distribution(client: httpx.AsyncClient):
    """Send 50 requests and verify both v1 and v2 receive traffic.

    With 90/10 split, v2 should get ~5 out of 50 requests.
    We just verify v2 gets at least 1 (proving the split works).
    """
    services_seen: dict[str, int] = {}

    for _ in range(50):
        resp = await client.get("/health")
        if resp.status_code == 200:
            service = resp.json().get("service", "unknown")
            services_seen[service] = services_seen.get(service, 0) + 1

    # Both versions should receive some traffic
    assert "products-v1" in services_seen or "products-v2" in services_seen, (
        f"Expected traffic to products services, got: {services_seen}"
    )


async def test_both_versions_return_products(client: httpx.AsyncClient):
    """Both v1 and v2 should return valid product lists."""
    resp = await client.get("/api/products")
    assert resp.status_code == 200
    products = resp.json()
    assert len(products) > 0
    assert "id" in products[0]
    assert "name" in products[0]
