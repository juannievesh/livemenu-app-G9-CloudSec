from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.request_logging import RequestLoggingMiddleware


@pytest.mark.asyncio
async def test_logging_middleware_calls_next():
    mw = RequestLoggingMiddleware.__new__(RequestLoggingMiddleware)

    request = MagicMock()
    request.method = "GET"
    request.url.path = "/api/v1/test"
    request.client.host = "127.0.0.1"

    response = MagicMock()
    response.status_code = 200

    call_next = AsyncMock(return_value=response)

    with patch("app.core.request_logging.logger") as mock_logger:
        result = await mw.dispatch(request, call_next)

    call_next.assert_awaited_once_with(request)
    assert result == response
    mock_logger.info.assert_called_once()


@pytest.mark.asyncio
async def test_logging_middleware_no_client():
    mw = RequestLoggingMiddleware.__new__(RequestLoggingMiddleware)

    request = MagicMock()
    request.method = "POST"
    request.url.path = "/api/v1/auth/login"
    request.client = None

    response = MagicMock()
    response.status_code = 201
    call_next = AsyncMock(return_value=response)

    with patch("app.core.request_logging.logger"):
        result = await mw.dispatch(request, call_next)

    assert result.status_code == 201
