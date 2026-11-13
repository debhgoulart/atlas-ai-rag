"""Pytest test configuration and shared async fixtures."""

import os
import sys
from typing import AsyncGenerator

# Ensure backend root is on Python module search path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Specify asyncio backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous HTTP client for endpoint testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
