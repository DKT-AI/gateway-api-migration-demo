import httpx
import pytest
from httpx import ASGITransport

from products_v1.main import app

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
    assert data["service"] == "products-v1"


async def test_list_products(client: httpx.AsyncClient):
    resp = await client.get("/api/products")
    assert resp.status_code == 200
    products = resp.json()
    assert isinstance(products, list)
    assert len(products) == 5
    assert products[0]["name"] == "Wireless Keyboard"


async def test_get_product(client: httpx.AsyncClient):
    resp = await client.get("/api/products/1")
    assert resp.status_code == 200
    product = resp.json()
    assert product["id"] == 1
    assert product["name"] == "Wireless Keyboard"
    assert product["price"] == 49.99


async def test_get_product_not_found(client: httpx.AsyncClient):
    resp = await client.get("/api/products/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Product not found"


async def test_all_products_have_required_fields(client: httpx.AsyncClient):
    resp = await client.get("/api/products")
    for product in resp.json():
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "category" in product
