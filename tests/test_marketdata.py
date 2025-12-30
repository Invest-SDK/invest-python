# pylint: disable=redefined-outer-name,unused-variable
# pylint: disable=protected-access
from unittest import mock

import pytest
from google.protobuf.json_format import MessageToDict

from t_tech.invest._grpc_helpers import dataclass_to_protobuf
from t_tech.invest.grpc import (
    GetCandlesRequest,
    GetLastPricesRequest,
    GetMySubscriptions,
    MarketDataRequest,
    MarketDataService,
    SubscribeTradesRequest,
    SubscriptionAction,
    TradeInstrument,
    marketdata_pb2,
)


@pytest.fixture()
def market_data_service():
    return mock.create_autospec(spec=MarketDataService)


def test_get_candles(market_data_service):
    response = market_data_service.get_candles(  # noqa: F841
        GetCandlesRequest(
            figi=mock.Mock(),
            from_=mock.Mock(),
            to=mock.Mock(),
            interval=mock.Mock(),
        )
    )
    market_data_service.get_candles.assert_called_once()


def test_get_last_prices(market_data_service):
    response = market_data_service.get_last_prices(  # noqa: F841
        GetLastPricesRequest(
            figi=mock.Mock(),
        )
    )
    market_data_service.get_last_prices.assert_called_once()


def test_get_order_book(market_data_service):
    response = market_data_service.get_order_book(request=mock.Mock())  # noqa: F841
    market_data_service.get_order_book.assert_called_once()


def test_get_trading_status(market_data_service):
    response = market_data_service.get_trading_status(request=mock.Mock())  # noqa: F841
    market_data_service.get_trading_status.assert_called_once()


def test_subscribe_trades_request():
    expected = marketdata_pb2.MarketDataRequest(
        subscribe_trades_request=marketdata_pb2.SubscribeTradesRequest(
            instruments=[marketdata_pb2.TradeInstrument(figi="figi")],
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
            with_open_interest=True,
        )
    )

    result = dataclass_to_protobuf(
        MarketDataRequest(
            subscribe_trades_request=SubscribeTradesRequest(
                instruments=[TradeInstrument(figi="figi")],
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                with_open_interest=True,
            )
        ),
        marketdata_pb2.MarketDataRequest(),
    )

    assert MessageToDict(result) == MessageToDict(expected)


def test_market_data_request_get_my_subscriptions():
    expected = marketdata_pb2.MarketDataRequest(
        get_my_subscriptions=marketdata_pb2.GetMySubscriptions()
    )

    result = dataclass_to_protobuf(
        MarketDataRequest(get_my_subscriptions=GetMySubscriptions()),
        marketdata_pb2.MarketDataRequest(),
    )

    assert MessageToDict(result) == MessageToDict(expected)
