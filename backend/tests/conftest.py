"""Test config — shared fixtures for pytest."""
from __future__ import annotations

import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
