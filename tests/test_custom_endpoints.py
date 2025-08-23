"""Tests for custom MCP endpoints added to the server."""

import json
from unittest.mock import Mock

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse

from kong_mcp_server.server import api_discovery, apis_discovery, sse_ping, sse_request


@pytest.mark.asyncio
async def test_api_discovery():
    """Test /api discovery endpoint."""
    request = Mock(spec=Request)
    response = await api_discovery(request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200

    # Parse response body
    body = json.loads(response.body)
    assert body["name"] == "Kong Rate Limiter MCP Server"
    assert body["version"] == "0.1.2"
    assert body["protocol_version"] == "2025-06-18"
    assert body["capabilities"]["tools"] is True
    assert "endpoints" in body


@pytest.mark.asyncio
async def test_apis_discovery():
    """Test /apis alternative discovery endpoint."""
    request = Mock(spec=Request)
    response = await apis_discovery(request)

    # Should be identical to api_discovery
    api_response = await api_discovery(request)
    assert response.body == api_response.body


@pytest.mark.asyncio
async def test_sse_ping():
    """Test /sse/ping endpoint."""
    request = Mock(spec=Request)
    response = await sse_ping(request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200

    body = json.loads(response.body)
    assert body["jsonrpc"] == "2.0"
    assert body["method"] == "ping"
    assert body["result"]["status"] == "ok"
    assert "timestamp" in body["result"]


@pytest.mark.asyncio
async def test_sse_request_default():
    """Test /sse/request endpoint with default request."""
    request = Mock(spec=Request)

    async def mock_json():
        return {"jsonrpc": "2.0", "method": "test_method", "id": 1}

    request.json = mock_json

    response = await sse_request(request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200

    body = json.loads(response.body)
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == 1
    assert body["result"]["status"] == "received"


@pytest.mark.asyncio
async def test_sse_request_tool_call():
    """Test /sse/request endpoint with tool call."""
    request = Mock(spec=Request)

    async def mock_json():
        return {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "test_tool"},
            "id": 1,
        }

    request.json = mock_json

    response = await sse_request(request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200

    body = json.loads(response.body)
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == 1
    assert "content" in body["result"]
    assert len(body["result"]["content"]) > 0


@pytest.mark.asyncio
async def test_sse_request_error_handling():
    """Test /sse/request endpoint error handling."""
    request = Mock(spec=Request)
    request.json = Mock(side_effect=Exception("Invalid JSON"))

    response = await sse_request(request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500

    body = json.loads(response.body)
    assert body["jsonrpc"] == "2.0"
    assert "error" in body
    assert body["error"]["code"] == -32603
