"""Pytest fixtures — in-memory repos, test settings, httpx test clients."""

import pytest

from sentinel_core.config.settings import Settings


@pytest.fixture
def test_settings() -> Settings:
    return Settings(mongodb_uri="mongodb://localhost:27017/sentinel_test")
