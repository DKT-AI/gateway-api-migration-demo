import httpx
import pytest
from httpx import ASGITransport

from cart.data import clear_carts
from cart.main import app

transport = ASGITransport(app=app)


@pytest.fixture(autouse=True)
def reset_carts():
    clear_carts()
    yield
    clear_carts()


@pytest.fixture
def client():
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_health(client: httpx.AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cart"


async def test_get_empty_cart(client: httpx.AsyncClient):
    resp = await client.get("/api/cart/user-1")
    assert resp.status_code == 200
    cart = resp.json()
    assert cart["user_id"] == "user-1"
    assert cart["items"] == []
    assert cart["total"] == 0


async def test_add_item_to_cart(client: httpx.AsyncClient):
    resp = await client.post(
        "/api/cart",
        json={
            "user_id": "user-1",
            "product_id": 1,
            "name": "Wireless Keyboard",
            "price": 49.99,
            "quantity": 1,
        },
    )
    assert resp.status_code == 200
    cart = resp.json()
    assert cart["user_id"] == "user-1"
    assert len(cart["items"]) == 1
    assert cart["items"][0]["product_id"] == 1
    assert cart["total"] == 49.99


async def test_add_multiple_items(client: httpx.AsyncClient):
    await client.post(
        "/api/cart",
        json={
            "user_id": "user-1",
            "product_id": 1,
            "name": "Wireless Keyboard",
            "price": 49.99,
            "quantity": 1,
        },
    )
    resp = await client.post(
        "/api/cart",
        json={
            "user_id": "user-1",
            "product_id": 2,
            "name": "USB-C Hub",
            "price": 29.99,
            "quantity": 1,
        },
    )
    cart = resp.json()
    assert len(cart["items"]) == 2
    assert cart["total"] == 79.98


async def test_add_same_item_increases_quantity(client: httpx.AsyncClient):
    await client.post(
        "/api/cart",
        json={
            "user_id": "user-1",
            "product_id": 1,
            "name": "Wireless Keyboard",
            "price": 49.99,
            "quantity": 1,
        },
    )
    resp = await client.post(
        "/api/cart",
        json={
            "user_id": "user-1",
            "product_id": 1,
            "name": "Wireless Keyboard",
            "price": 49.99,
            "quantity": 2,
        },
    )
    cart = resp.json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 3
    assert cart["total"] == 149.97


async def test_separate_user_carts(client: httpx.AsyncClient):
    await client.post(
        "/api/cart",
        json={
            "user_id": "user-1",
            "product_id": 1,
            "name": "Wireless Keyboard",
            "price": 49.99,
        },
    )
    await client.post(
        "/api/cart",
        json={
            "user_id": "user-2",
            "product_id": 2,
            "name": "USB-C Hub",
            "price": 29.99,
        },
    )
    resp1 = await client.get("/api/cart/user-1")
    resp2 = await client.get("/api/cart/user-2")
    assert len(resp1.json()["items"]) == 1
    assert len(resp2.json()["items"]) == 1
    assert resp1.json()["items"][0]["product_id"] == 1
    assert resp2.json()["items"][0]["product_id"] == 2
