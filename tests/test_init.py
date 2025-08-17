"""Tests for package initialization."""

import kong_mcp_server


def test_package_has_version() -> None:
    """Test that package has a version attribute."""
    assert hasattr(kong_mcp_server, "__version__")
    assert isinstance(kong_mcp_server.__version__, str)


def test_version_is_not_empty() -> None:
    """Test that version is not empty."""
    assert kong_mcp_server.__version__ != ""
    assert kong_mcp_server.__version__ is not None
