import httpx
import pytest
from httpx import ASGITransport

from products_v2.main import app

transport = ASGITransport(app=app)


@pytest.fixture
async def client():
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_health(client: httpx.AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "products-v2"


async def test_list_products(client: httpx.AsyncClient):
    resp = await client.get("/api/products")
    assert resp.status_code == 200
    products = resp.json()
    assert isinstance(products, list)
    assert len(products) == 5


async def test_get_product(client: httpx.AsyncClient):
    resp = await client.get("/api/products/1")
    assert resp.status_code == 200
    product = resp.json()
    assert product["id"] == 1
    assert product["name"] == "Wireless Keyboard"


async def test_get_product_not_found(client: httpx.AsyncClient):
    resp = await client.get("/api/products/999")
    assert resp.status_code == 404


async def test_recommendations(client: httpx.AsyncClient):
    resp = await client.get("/api/products/1/recommendations")
    assert resp.status_code == 200
    recs = resp.json()
    assert isinstance(recs, list)
    assert len(recs) >= 1
    assert "reason" in recs[0]


async def test_recommendations_for_product_without_recs(client: httpx.AsyncClient):
    # Product 5 has recommendations, but a non-existent product should 404
    resp = await client.get("/api/products/999/recommendations")
    assert resp.status_code == 404


async def test_recommendations_have_required_fields(client: httpx.AsyncClient):
    resp = await client.get("/api/products/1/recommendations")
    for rec in resp.json():
        assert "id" in rec
        assert "name" in rec
        assert "price" in rec
        assert "reason" in rec
