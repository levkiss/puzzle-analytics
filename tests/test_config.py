"""Tests for configuration module."""

import pytest

from puzzle_swap_etl.config import Settings


def test_settings_creation():
    """Test that settings can be created with defaults."""
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5432/test"
    )

    assert settings.database_url == "postgresql+asyncpg://test:test@localhost:5432/test"
    assert settings.waves_node_url == "https://nodes.wx.network/"
    assert settings.puzzle_token_id == "HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS"
    assert settings.batch_size == 1000
    assert settings.log_level == "INFO"


def test_waves_node_urls_property():
    """Test that waves_node_urls property returns list of URLs."""
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5432/test"
    )

    urls = settings.waves_node_urls
    assert isinstance(urls, list)
    assert len(urls) == 2
    assert settings.waves_node_url in urls
    assert settings.waves_node_backup_url in urls


def test_settings_validation():
    """Test settings validation."""
    # Test invalid batch size
    with pytest.raises(ValueError):
        Settings(
            database_url="postgresql+asyncpg://test:test@localhost:5432/test",
            batch_size=0,
        )

    # Test invalid log level
    with pytest.raises(ValueError):
        Settings(
            database_url="postgresql+asyncpg://test:test@localhost:5432/test",
            log_level="INVALID",
        )
