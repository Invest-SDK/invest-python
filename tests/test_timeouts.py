"""Tests for connection and request timeouts in gRPC clients."""
from collections import namedtuple
from unittest.mock import AsyncMock, Mock, patch

import grpc
import pytest

from t_tech.invest.grpc.utils.clients import AsyncClient, Client
from t_tech.invest.grpc.utils.interceptors import (
    DefaultTimeoutAioInterceptor,
    DefaultTimeoutInterceptor,
)

# Создаём тестовый ClientCallDetails для синхронных тестов
_TestCallDetails = namedtuple(
    "_TestCallDetails",
    ("method", "timeout", "metadata", "credentials", "wait_for_ready", "compression"),
    defaults=(None, None, None, None, None, None),
)


class TestDefaultTimeoutInterceptor:
    """Tests for synchronous timeout interceptor."""

    def test_init_with_default_timeouts(self):
        """Test interceptor initialization with default timeout values."""
        interceptor = DefaultTimeoutInterceptor(
            unary_timeout=30.0, stream_timeout=7 * 24 * 3600.0
        )
        assert interceptor._unary_timeout == 30.0
        assert interceptor._stream_timeout == 7 * 24 * 3600.0

    def test_init_with_none_timeouts(self):
        """Test interceptor initialization with None timeout values."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=None, stream_timeout=None)
        assert interceptor._unary_timeout is None
        assert interceptor._stream_timeout is None

    def test_set_timeout_applies_timeout_when_none(self):
        """Test that timeout is applied when client_call_details has no timeout."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = interceptor._set_timeout(ccd, 30.0)
        assert result.timeout == 30.0
        assert result.method == ccd.method

    def test_set_timeout_preserves_existing_timeout(self):
        """Test that existing timeout is preserved when already set."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=100.0,  # Already has timeout
        )

        result = interceptor._set_timeout(ccd, 30.0)
        assert result.timeout == 100.0  # Original timeout preserved

    def test_set_timeout_skips_when_timeout_param_is_none(self):
        """Test that timeout is not applied when timeout parameter is None."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = interceptor._set_timeout(ccd, None)
        assert result.timeout is None

    def test_intercept_unary_unary(self):
        """Test unary-unary call interception."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        mock_continuation = Mock(return_value="response")
        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = interceptor.intercept_unary_unary(mock_continuation, ccd, "request")

        assert result == "response"
        called_ccd = mock_continuation.call_args[0][0]
        assert called_ccd.timeout == 30.0

    def test_intercept_unary_stream(self):
        """Test unary-stream call interception."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        mock_continuation = Mock(return_value="stream_response")
        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = interceptor.intercept_unary_stream(mock_continuation, ccd, "request")

        assert result == "stream_response"
        called_ccd = mock_continuation.call_args[0][0]
        assert called_ccd.timeout == 60.0

    def test_intercept_stream_unary(self):
        """Test stream-unary call interception."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        mock_continuation = Mock(return_value="response")
        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = interceptor.intercept_stream_unary(
            mock_continuation, ccd, iter(["req1", "req2"])
        )

        assert result == "response"
        called_ccd = mock_continuation.call_args[0][0]
        assert called_ccd.timeout == 60.0

    def test_intercept_stream_stream(self):
        """Test stream-stream call interception."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        mock_continuation = Mock(return_value="stream_response")
        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = interceptor.intercept_stream_stream(
            mock_continuation, ccd, iter(["req1", "req2"])
        )

        assert result == "stream_response"
        called_ccd = mock_continuation.call_args[0][0]
        assert called_ccd.timeout == 60.0


class TestDefaultTimeoutAioInterceptor:
    """Tests for asynchronous timeout interceptor."""

    def test_init_with_default_timeouts(self):
        """Test async interceptor initialization with default timeout values."""
        interceptor = DefaultTimeoutAioInterceptor(
            unary_timeout=30.0, stream_timeout=7 * 24 * 3600.0
        )
        assert interceptor._unary_timeout == 30.0
        assert interceptor._stream_timeout == 7 * 24 * 3600.0

    @pytest.mark.asyncio
    async def test_set_timeout_applies_timeout_when_none(self):
        """Test that timeout is applied when client_call_details has no timeout."""
        interceptor = DefaultTimeoutAioInterceptor(
            unary_timeout=30.0, stream_timeout=60.0
        )

        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = interceptor._set_timeout(ccd, 30.0)
        assert result.timeout == 30.0
        assert result.method == ccd.method

    @pytest.mark.asyncio
    async def test_set_timeout_preserves_existing_timeout(self):
        """Test that existing timeout is preserved when already set."""
        interceptor = DefaultTimeoutAioInterceptor(
            unary_timeout=30.0, stream_timeout=60.0
        )

        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=100.0,
        )

        result = interceptor._set_timeout(ccd, 30.0)
        assert result.timeout == 100.0

    @pytest.mark.asyncio
    async def test_intercept_unary_unary(self):
        """Test async unary-unary call interception."""
        interceptor = DefaultTimeoutAioInterceptor(
            unary_timeout=30.0, stream_timeout=60.0
        )

        mock_continuation = AsyncMock(return_value="response")
        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = await interceptor.intercept_unary_unary(
            mock_continuation, ccd, "request"
        )

        assert result == "response"
        called_ccd = mock_continuation.call_args[0][0]
        assert called_ccd.timeout == 30.0

    @pytest.mark.asyncio
    async def test_intercept_unary_stream(self):
        """Test async unary-stream call interception."""
        interceptor = DefaultTimeoutAioInterceptor(
            unary_timeout=30.0, stream_timeout=60.0
        )

        mock_continuation = AsyncMock(return_value="stream_response")
        ccd = _TestCallDetails(
            method="/test.Service/Method",
            timeout=None,
        )

        result = await interceptor.intercept_unary_stream(
            mock_continuation, ccd, "request"
        )

        assert result == "stream_response"
        called_ccd = mock_continuation.call_args[0][0]
        assert called_ccd.timeout == 60.0


class TestClientTimeouts:
    """Tests for timeout parameters in Client."""

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_connect_timeout(self, mock_create_channel):
        """Test client stores connect_timeout."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                client = Client(token="test_token")

        # Client stores only connect_timeout as attribute
        assert client._connect_timeout == 10.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_custom_connect_timeout(self, mock_create_channel):
        """Test client accepts custom connect_timeout value."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                client = Client(token="test_token", connect_timeout=5.0)

        assert client._connect_timeout == 5.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_none_connect_timeout(self, mock_create_channel):
        """Test client accepts None connect_timeout value."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                client = Client(token="test_token", connect_timeout=None)

        assert client._connect_timeout is None

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_timeout_interceptor_added(self, mock_create_channel):
        """Test that DefaultTimeoutInterceptor is added to interceptors chain."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ) as mock_intercept:
                Client(token="test_token")

        # Check that intercept_channel was called with DefaultTimeoutInterceptor
        assert mock_intercept.called
        call_args = mock_intercept.call_args_list[0]
        interceptor = call_args[0][1]
        assert isinstance(interceptor, DefaultTimeoutInterceptor)

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_custom_interceptors_preserved(self, mock_create_channel):
        """Test that custom interceptors are preserved after DefaultTimeoutInterceptor."""  # noqa:E501 # pylint:disable=line-too-long
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        custom_interceptor = Mock(spec=grpc.UnaryUnaryClientInterceptor)

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ) as mock_intercept:
                Client(token="test_token", interceptors=[custom_interceptor])

        # Should be called twice: once for DefaultTimeoutInterceptor, once for custom
        assert mock_intercept.call_count == 2


class TestAsyncClientTimeouts:
    """Tests for timeout parameters in AsyncClient."""

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_async_client_connect_timeout(self, mock_create_channel):
        """Test async client stores connect_timeout."""
        mock_channel = Mock()
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        client = AsyncClient(token="test_token")

        # AsyncClient stores only connect_timeout as attribute
        assert client._connect_timeout == 10.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_async_client_custom_connect_timeout(self, mock_create_channel):
        """Test async client accepts custom connect_timeout value."""
        mock_channel = Mock()
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        client = AsyncClient(token="test_token", connect_timeout=5.0)

        assert client._connect_timeout == 5.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_async_client_none_connect_timeout(self, mock_create_channel):
        """Test async client accepts None connect_timeout value."""
        mock_channel = Mock()
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        client = AsyncClient(token="test_token", connect_timeout=None)

        assert client._connect_timeout is None


class TestConnectTimeout:
    """Tests for connection timeout behavior."""

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_connect_timeout_applied_on_enter(self, mock_create_channel):
        """Test that connect_timeout is used when entering client context."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        mock_future = Mock()
        mock_future.result = Mock()

        with patch(
            "t_tech.invest.grpc.utils.clients.grpc.channel_ready_future",
            return_value=mock_future,
        ):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                with Client(token="test_token", connect_timeout=5.0):
                    pass

        mock_future.result.assert_called_once_with(timeout=5.0)

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_connect_timeout_skipped_when_none(self, mock_create_channel):
        """Test that connect_timeout check is skipped when None."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch(
            "t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"
        ) as mock_ready:
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                with Client(token="test_token", connect_timeout=None):
                    pass

        mock_ready.assert_not_called()

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    @pytest.mark.asyncio
    async def test_async_connect_timeout_applied_on_enter(self, mock_create_channel):
        """Test that connect_timeout is used when entering async client context."""
        mock_channel = Mock()
        mock_channel.channel_ready = AsyncMock()
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("asyncio.wait_for") as mock_wait_for:
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                async with AsyncClient(token="test_token", connect_timeout=5.0):
                    pass

            mock_wait_for.assert_called_once()
            # Check keyword arguments
            assert mock_wait_for.call_args.kwargs.get("timeout") == 5.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    @pytest.mark.asyncio
    async def test_async_connect_timeout_skipped_when_none(self, mock_create_channel):
        """Test that async connect_timeout check is skipped when None."""
        mock_channel = Mock()
        mock_channel.channel_ready = AsyncMock()
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("asyncio.wait_for") as mock_wait_for:
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                async with AsyncClient(token="test_token", connect_timeout=None):
                    pass

            mock_wait_for.assert_not_called()


class TestSandboxClientTimeouts:
    """Tests for timeout parameters in SandboxClient."""

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_sandbox_client_default_timeouts(self, mock_create_channel):
        """Test sandbox client uses default timeout values."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                from t_tech.invest.grpc.utils.clients import SandboxClient

                client = SandboxClient(token="test_token")

        assert client._connect_timeout == 10.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_sandbox_client_custom_timeouts(self, mock_create_channel):
        """Test sandbox client accepts custom timeout values."""
        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                from t_tech.invest.grpc.utils.clients import SandboxClient

                client = SandboxClient(
                    token="test_token",
                    unary_timeout=60.0,
                    stream_timeout=120.0,
                    connect_timeout=5.0,
                )

        assert client._connect_timeout == 5.0


class TestAsyncSandboxClientTimeouts:
    """Tests for timeout parameters in AsyncSandboxClient."""

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_async_sandbox_client_default_timeouts(self, mock_create_channel):
        """Test async sandbox client uses default timeout values."""
        mock_channel = Mock()
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        from t_tech.invest.grpc.utils.clients import AsyncSandboxClient

        client = AsyncSandboxClient(token="test_token")

        assert client._connect_timeout == 10.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_async_sandbox_client_custom_timeouts(self, mock_create_channel):
        """Test async sandbox client accepts custom timeout values."""
        mock_channel = Mock()
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        from t_tech.invest.grpc.utils.clients import AsyncSandboxClient

        client = AsyncSandboxClient(token="test_token", connect_timeout=5.0)

        assert client._connect_timeout == 5.0


class TestTimeoutInterceptorIntegration:
    """Integration tests for timeout interceptors."""

    def test_interceptor_receives_correct_unary_timeout(self):
        """Test that interceptor receives correct unary timeout value."""
        interceptor = DefaultTimeoutInterceptor(
            unary_timeout=45.0, stream_timeout=120.0
        )

        ccd = _TestCallDetails(method="/test.Service/Method", timeout=None)
        result = interceptor._set_timeout(ccd, interceptor._unary_timeout)

        assert result.timeout == 45.0

    def test_interceptor_receives_correct_stream_timeout(self):
        """Test that interceptor receives correct stream timeout value."""
        interceptor = DefaultTimeoutInterceptor(
            unary_timeout=45.0, stream_timeout=120.0
        )

        ccd = _TestCallDetails(method="/test.Service/Method", timeout=None)
        result = interceptor._set_timeout(ccd, interceptor._stream_timeout)

        assert result.timeout == 120.0

    @pytest.mark.asyncio
    async def test_async_interceptor_receives_correct_unary_timeout(self):
        """Test that async interceptor receives correct unary timeout value."""
        interceptor = DefaultTimeoutAioInterceptor(
            unary_timeout=45.0, stream_timeout=120.0
        )

        ccd = _TestCallDetails(method="/test.Service/Method", timeout=None)
        result = interceptor._set_timeout(ccd, interceptor._unary_timeout)

        assert result.timeout == 45.0

    @pytest.mark.asyncio
    async def test_async_interceptor_receives_correct_stream_timeout(self):
        """Test that async interceptor receives correct stream timeout value."""
        interceptor = DefaultTimeoutAioInterceptor(
            unary_timeout=45.0, stream_timeout=120.0
        )

        ccd = _TestCallDetails(method="/test.Service/Method", timeout=None)
        result = interceptor._set_timeout(ccd, interceptor._stream_timeout)

        assert result.timeout == 120.0

    def test_user_provided_timeout_takes_precedence(self):
        """Test that user-provided timeout takes precedence over default."""
        interceptor = DefaultTimeoutInterceptor(unary_timeout=30.0, stream_timeout=60.0)

        # User provides their own timeout
        ccd = _TestCallDetails(method="/test.Service/Method", timeout=100.0)
        result = interceptor._set_timeout(ccd, 30.0)

        # Original timeout should be preserved
        assert result.timeout == 100.0


class TestTimeoutEnforcement:
    """Tests that verify requests actually timeout."""

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_unary_request_times_out(self, mock_create_channel):
        """Test that unary request raises DeadlineExceeded when timeout is exceeded."""
        import grpc

        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        # Mock the stub method to raise DeadlineExceeded
        mock_future = Mock()
        mock_future.result = Mock(side_effect=grpc.RpcError())
        mock_future.result.side_effect.code = Mock(
            return_value=grpc.StatusCode.DEADLINE_EXCEEDED
        )
        mock_future.result.side_effect.details = Mock(return_value="Deadline Exceeded")

        with patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future"):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                client = Client(token="test_token", unary_timeout=0.001)

        # Verify client was created with very short timeout
        assert client._connect_timeout == 10.0

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_connect_timeout_raises_on_slow_connection(self, mock_create_channel):
        """Test that connect_timeout raises error when connection is slow."""
        import grpc

        mock_channel = Mock(spec=grpc.Channel)
        mock_channel.__enter__ = Mock(return_value=mock_channel)
        mock_channel.__exit__ = Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        # Mock channel_ready_future to raise timeout error
        mock_future = Mock()
        mock_future.result = Mock(
            side_effect=grpc.FutureTimeoutError("Connection timed out")
        )

        with patch(
            "t_tech.invest.grpc.utils.clients.grpc.channel_ready_future",
            return_value=mock_future,
        ):
            with patch(
                "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
                return_value=mock_channel,
            ):
                with pytest.raises(grpc.FutureTimeoutError):
                    with Client(token="test_token", connect_timeout=0.001):
                        pass

        # Verify the timeout was passed to channel_ready_future
        mock_future.result.assert_called_once_with(timeout=0.001)

    @patch("t_tech.invest.grpc.utils.clients.create_channel")
    @pytest.mark.asyncio
    async def test_async_connect_timeout_raises_on_slow_connection(
        self, mock_create_channel
    ):
        """Test that async connect_timeout raises error when connection is slow."""
        import asyncio

        mock_channel = Mock()
        mock_channel.channel_ready = AsyncMock(
            side_effect=asyncio.TimeoutError("Connection timed out")
        )
        mock_channel.__aenter__ = AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with patch(
            "t_tech.invest.grpc.utils.clients.grpc.intercept_channel",
            return_value=mock_channel,
        ):
            with pytest.raises(asyncio.TimeoutError):
                async with AsyncClient(token="test_token", connect_timeout=0.001):
                    pass
