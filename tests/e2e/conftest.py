"""E2E test configuration.

These tests run against a live EKS cluster.
Set BASE_URL env var or use --base-url pytest flag.
"""

import os

import httpx
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        default=os.environ.get("BASE_URL", "https://gateway-demo.vedmich.dev"),
        help="Base URL of the live cluster",
    )


@pytest.fixture
def base_url(request: pytest.FixtureRequest) -> str:
    url = str(request.config.getoption("--base-url"))
    return url


@pytest.fixture
async def client(base_url: str):
    async with httpx.AsyncClient(base_url=base_url, verify=True, timeout=10.0) as c:
        yield c
