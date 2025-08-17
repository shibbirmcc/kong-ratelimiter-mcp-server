"""Tests for Kong MCP Server."""

from unittest.mock import Mock, patch

from kong_mcp_server.server import (
    load_tools_config,
    mcp,
    register_tool,
    setup_tools,
)


def test_mcp_server_creation() -> None:
    """Test that MCP server is properly created."""
    assert mcp.name == "Kong Rate Limiter MCP Server"
    assert mcp is not None


def test_mcp_server_is_fastmcp_instance() -> None:
    """Test that MCP server is a FastMCP instance."""
    from fastmcp import FastMCP

    assert isinstance(mcp, FastMCP)


def test_load_tools_config() -> None:
    """Test loading tools configuration from JSON file."""
    config = load_tools_config()

    assert "tools" in config
    assert isinstance(config["tools"], dict)
    assert "hello_world" in config["tools"]

    hello_world_config = config["tools"]["hello_world"]
    assert hello_world_config["name"] == "hello_world"
    assert hello_world_config["module"] == "kong_mcp_server.tools.basic"
    assert hello_world_config["function"] == "hello_world"
    assert hello_world_config["enabled"] is True


@patch("builtins.open")
@patch("kong_mcp_server.server.json.load")
def test_load_tools_config_with_mock(
    mock_json_load: Mock, mock_open: Mock
) -> None:
    """Test loading tools configuration using mocks."""
    test_config = {
        "tools": {
            "test_tool": {
                "name": "test_tool",
                "description": "Test tool",
                "module": "test.module",
                "function": "test_function",
                "enabled": True,
            }
        }
    }

    mock_json_load.return_value = test_config

    config = load_tools_config()

    mock_open.assert_called_once()
    mock_json_load.assert_called_once()
    assert config == test_config


@patch("kong_mcp_server.server.importlib.import_module")
def test_register_tool_success(mock_import: Mock) -> None:
    """Test successful tool registration."""
    mock_module = Mock()
    mock_function = Mock()
    mock_module.test_function = mock_function
    mock_import.return_value = mock_module

    tool_config = {
        "name": "test_tool",
        "description": "Test tool description",
        "module": "test.module",
        "function": "test_function",
    }

    with patch.object(mcp, "tool") as mock_tool:
        mock_decorator = Mock()
        mock_tool.return_value = mock_decorator

        register_tool(tool_config)

        mock_import.assert_called_once_with("test.module")
        mock_tool.assert_called_once_with(
            name="test_tool", description="Test tool description"
        )
        mock_decorator.assert_called_once_with(mock_function)


@patch("kong_mcp_server.server.importlib.import_module")
@patch("builtins.print")
def test_register_tool_import_error(
    mock_print: Mock, mock_import: Mock
) -> None:
    """Test tool registration with import error."""
    mock_import.side_effect = ImportError("Module not found")

    tool_config = {
        "name": "test_tool",
        "description": "Test tool description",
        "module": "nonexistent.module",
        "function": "test_function",
    }

    register_tool(tool_config)

    mock_print.assert_called_once_with(
        "Warning: Could not load tool test_tool: Module not found"
    )


@patch("kong_mcp_server.server.importlib.import_module")
@patch("builtins.print")
def test_register_tool_attribute_error(
    mock_print: Mock, mock_import: Mock
) -> None:
    """Test tool registration with attribute error."""
    mock_module = Mock(spec=[])  # Empty spec means no attributes
    mock_import.return_value = mock_module

    tool_config = {
        "name": "test_tool",
        "description": "Test tool description",
        "module": "test.module",
        "function": "nonexistent_function",
    }

    register_tool(tool_config)

    mock_print.assert_called_once_with(
        "Warning: Could not load tool test_tool: "
        "Mock object has no attribute 'nonexistent_function'"
    )


@patch("kong_mcp_server.server.load_tools_config")
@patch("kong_mcp_server.server.register_tool")
def test_setup_tools(mock_register: Mock, mock_load_config: Mock) -> None:
    """Test setup of all enabled tools."""
    mock_config = {
        "tools": {
            "enabled_tool": {"name": "enabled_tool", "enabled": True},
            "disabled_tool": {"name": "disabled_tool", "enabled": False},
            "default_disabled_tool": {
                "name": "default_disabled_tool"
                # No 'enabled' key defaults to False
            },
        }
    }
    mock_load_config.return_value = mock_config

    setup_tools()

    mock_load_config.assert_called_once()
    mock_register.assert_called_once_with(
        {"name": "enabled_tool", "enabled": True}
    )
