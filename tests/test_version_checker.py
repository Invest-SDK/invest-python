# pylint: disable=redefined-outer-name,unused-variable,protected-access
"""Tests for SDK version checking functionality."""

import warnings
from unittest import mock

import pytest
import requests

from t_tech.invest._version_checker import (
    check_version,
    get_current_version,
    get_latest_version,
    get_version_warning,
    parse_version,
)


class TestParseVersion:
    """Tests for parse_version function."""

    def test_parse_standard_version(self):
        """Test parsing standard version string."""
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_parse_version_with_v_prefix(self):
        """Test parsing version string with 'v' prefix."""
        assert parse_version("v1.2.3") == (1, 2, 3)

    def test_parse_two_part_version(self):
        """Test parsing two-part version string."""
        assert parse_version("1.2") == (1, 2)

    def test_parse_invalid_version_returns_zeros(self):
        """Test that invalid version strings return (0, 0, 0)."""
        assert parse_version("invalid") == (0, 0, 0)


class TestGetCurrentVersion:
    """Tests for get_current_version function."""

    def test_get_current_version_returns_string(self):
        """Test that get_current_version returns a string."""
        version = get_current_version()
        assert isinstance(version, str)


class TestGetLatestVersion:
    """Tests for get_latest_version function."""

    @mock.patch("t_tech.invest._version_checker.requests.get")
    def test_get_latest_version_success(self, mock_get):
        """Test successful fetch of latest version."""
        mock_response = mock.Mock()
        mock_response.json.return_value = [
            {"tag_name": "v1.50.0", "name": "Release 1.50.0"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_latest_version()

        assert result == "1.50.0"
        mock_get.assert_called_once_with(
            "https://opensource.tbank.ru/api/v4/projects/238/releases",
            headers={"User-Agent": "tinkoff-invest-python-sdk"},
            timeout=5,
        )

    @mock.patch("t_tech.invest._version_checker.requests.get")
    def test_get_latest_version_empty_response(self, mock_get):
        """Test handling of empty response list."""
        mock_response = mock.Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_latest_version()

        assert result is None

    @mock.patch("t_tech.invest._version_checker.requests.get")
    def test_get_latest_version_invalid_release_format(self, mock_get):
        """Test handling of invalid release format."""
        mock_response = mock.Mock()
        mock_response.json.return_value = ["not a dict"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_latest_version()

        assert result is None

    @mock.patch("t_tech.invest._version_checker.requests.get")
    def test_get_latest_version_missing_tag_name(self, mock_get):
        """Test handling of missing tag_name field."""
        mock_response = mock.Mock()
        mock_response.json.return_value = [{"name": "Release"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_latest_version()

        assert result is None

    @mock.patch("t_tech.invest._version_checker.requests.get")
    def test_get_latest_version_network_error(self, mock_get):
        """Test handling of network error."""
        mock_get.side_effect = requests.RequestException("Network error")

        result = get_latest_version()

        assert result is None


class TestCheckVersion:
    """Tests for check_version function."""

    @mock.patch("t_tech.invest._version_checker.get_latest_version")
    def test_check_version_update_available(self, mock_get_latest):
        """Test that update is detected when latest version is newer."""
        mock_get_latest.return_value = "1.50.0"

        result = check_version("1.49.0")

        assert result == "1.50.0"

    @mock.patch("t_tech.invest._version_checker.get_latest_version")
    def test_check_version_no_update_same(self, mock_get_latest):
        """Test that no update is detected when versions are the same."""
        mock_get_latest.return_value = "1.49.0"

        result = check_version("1.49.0")

        assert result is None

    @mock.patch("t_tech.invest._version_checker.get_latest_version")
    def test_check_version_no_update_current_newer(self, mock_get_latest):
        """Test that no update is detected when current version is newer."""
        mock_get_latest.return_value = "1.48.0"

        result = check_version("1.49.0")

        assert result is None

    @mock.patch("t_tech.invest._version_checker.get_latest_version")
    def test_check_version_major_update(self, mock_get_latest):
        """Test detection of major version update."""
        mock_get_latest.return_value = "2.0.0"

        result = check_version("1.49.0")

        assert result == "2.0.0"

    @mock.patch("t_tech.invest._version_checker.get_latest_version")
    def test_check_version_no_latest_version(self, mock_get_latest):
        """Test handling when latest version cannot be fetched."""
        mock_get_latest.return_value = None

        result = check_version("1.49.0")

        assert result is None


class TestGetVersionWarning:
    """Tests for get_version_warning function."""

    @mock.patch("t_tech.invest._version_checker.get_current_version")
    @mock.patch("t_tech.invest._version_checker.check_version")
    def test_get_version_warning_returns_warning(self, mock_check, mock_current):
        """Test that warning is returned when update is available."""
        mock_current.return_value = "1.49.0"
        mock_check.return_value = "1.50.0"

        result = get_version_warning()

        assert result is not None
        assert "WARNING" in result
        assert "newer version" in result
        assert "1.49.0" in result
        assert "1.50.0" in result
        assert "t-tech-investments python SDK" in result

    @mock.patch("t_tech.invest._version_checker.get_current_version")
    @mock.patch("t_tech.invest._version_checker.check_version")
    def test_get_version_warning_no_update(self, mock_check, mock_current):
        """Test that None is returned when no update is available."""
        mock_current.return_value = "1.49.0"
        mock_check.return_value = None

        result = get_version_warning()

        assert result is None


class TestClientVersionWarning:
    """Tests for version warning on client initialization."""

    @mock.patch("t_tech.invest.grpc.utils.clients.get_version_warning")
    @mock.patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_init_shows_version_warning(self, mock_create_channel, mock_get_warning):
        """Test that Client initialization shows version warning."""
        from t_tech.invest.grpc import Client

        mock_get_warning.return_value = "WARNING: New version available"
        mock_channel = mock.Mock()
        mock_future = mock.Mock()
        mock_future.result.return_value = None
        mock_channel.__enter__ = mock.Mock(return_value=mock_channel)
        mock_channel.__exit__ = mock.Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        def mock_channel_ready_future(channel):
            return mock_future

        with mock.patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future", mock_channel_ready_future):
            with pytest.warns(UserWarning, match="New version available"):
                with Client(token="test_token", check_sdk_version=True):
                    pass

        mock_get_warning.assert_called_once()

    @mock.patch("t_tech.invest.grpc.utils.clients.get_version_warning")
    @mock.patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_init_no_warning_when_no_update(self, mock_create_channel, mock_get_warning):
        """Test that Client initialization does not show warning when no update."""
        from t_tech.invest.grpc import Client

        mock_get_warning.return_value = None
        mock_channel = mock.Mock()
        mock_future = mock.Mock()
        mock_future.result.return_value = None
        mock_channel.__enter__ = mock.Mock(return_value=mock_channel)
        mock_channel.__exit__ = mock.Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        def mock_channel_ready_future(channel):
            return mock_future

        with mock.patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future", mock_channel_ready_future):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                with Client(token="test_token", check_sdk_version=True):
                    pass
                # Check that no UserWarning was raised
                user_warnings = [warning for warning in w if issubclass(warning.category, UserWarning)]
                assert len(user_warnings) == 0

        mock_get_warning.assert_called_once()

    @mock.patch("t_tech.invest.grpc.utils.clients.get_version_warning")
    @mock.patch("t_tech.invest.grpc.utils.clients.create_channel")
    def test_client_init_version_check_disabled(self, mock_create_channel, mock_get_warning):
        """Test that Client initialization skips version check when disabled."""
        from t_tech.invest.grpc import Client

        mock_channel = mock.Mock()
        mock_future = mock.Mock()
        mock_future.result.return_value = None
        mock_channel.__enter__ = mock.Mock(return_value=mock_channel)
        mock_channel.__exit__ = mock.Mock(return_value=False)
        mock_create_channel.return_value = mock_channel

        def mock_channel_ready_future(channel):
            return mock_future

        with mock.patch("t_tech.invest.grpc.utils.clients.grpc.channel_ready_future", mock_channel_ready_future):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                with Client(token="test_token", check_sdk_version=False):
                    pass
                # Check that no UserWarning was raised
                user_warnings = [warning for warning in w if issubclass(warning.category, UserWarning)]
                assert len(user_warnings) == 0

        mock_get_warning.assert_not_called()

    @mock.patch("t_tech.invest.grpc.utils.clients.get_version_warning")
    @mock.patch("t_tech.invest.grpc.utils.clients.create_channel")
    @pytest.mark.asyncio
    async def test_async_client_init_shows_version_warning(self, mock_create_channel, mock_get_warning):
        """Test that AsyncClient initialization shows version warning."""
        from t_tech.invest.grpc import AsyncClient

        mock_get_warning.return_value = "WARNING: New version available"
        mock_channel = mock.AsyncMock()
        mock_channel.channel_ready = mock.AsyncMock()
        mock_channel.__aenter__ = mock.AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = mock.AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with pytest.warns(UserWarning, match="New version available"):
            async with AsyncClient(token="test_token", check_sdk_version=True):
                pass

        mock_get_warning.assert_called_once()

    @mock.patch("t_tech.invest.grpc.utils.clients.get_version_warning")
    @mock.patch("t_tech.invest.grpc.utils.clients.create_channel")
    @pytest.mark.asyncio
    async def test_async_client_init_no_warning_when_no_update(self, mock_create_channel, mock_get_warning):
        """Test that AsyncClient initialization does not show warning when no update."""
        from t_tech.invest.grpc import AsyncClient

        mock_get_warning.return_value = None
        mock_channel = mock.AsyncMock()
        mock_channel.channel_ready = mock.AsyncMock()
        mock_channel.__aenter__ = mock.AsyncMock(return_value=mock_channel)
        mock_channel.__aexit__ = mock.AsyncMock(return_value=False)
        mock_create_channel.return_value = mock_channel

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            async with AsyncClient(token="test_token", check_sdk_version=True):
                pass
            # Check that no UserWarning was raised
            user_warnings = [warning for warning in w if issubclass(warning.category, UserWarning)]
            assert len(user_warnings) == 0

        mock_get_warning.assert_called_once()
