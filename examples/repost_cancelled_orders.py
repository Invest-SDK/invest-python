"""Пример - повторное выставление лимитных заявок, отмененных на закрытии торгов.

Пример работает в трех режимах:

1. REPOST_MODE = "save"
   Сохраняет сегодняшние лимитные заявки, отмененные вблизи закрытия торгов,
   в локальный файл. Этот режим нужно запускать в тот же торговый день
   после закрытия торгов.

2. REPOST_MODE = "stop"
   Загружает сохраненные заявки за предыдущий торговый день и выставляет
   оставшийся объем как стоп-лимитные заявки.

3. REPOST_MODE = "limit_at_open"
   Загружает сохраненные заявки за предыдущий торговый день и выставляет
   оставшийся объем как лимитные заявки на старте следующих торгов.

Важно:
Методы GetOrders и TradingSchedules не позволяют запрашивать данные
за прошедшие даты. Поэтому заявки, отмененные на закрытии торгов,
нужно сохранить в день отмены, а на следующий день использовать
сохраненный локальный файл.
"""

import datetime
import json
import logging
import os
import time
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import (
    ExchangeOrderType,
    GetOrdersRequest,
    OrderDirection,
    OrderExecutionReportStatus,
    OrderType,
    PostOrderRequest,
    PostStopOrderRequest,
    Quotation,
    StopOrderDirection,
    StopOrderExpirationType,
    StopOrderType,
    TradingSchedulesRequest,
)
from t_tech.invest.grpc.utils.grpc_services import Services
from t_tech.invest.utils import now

TOKEN = os.environ["INVEST_TOKEN"]

EXCHANGE = "MOEX"

# "save", "stop" or "limit_at_open"
REPOST_MODE = "stop"

CLOSE_WINDOW = datetime.timedelta(minutes=30)
MOEX_CLOSE_TIME = datetime.time(hour=18, minute=50)
SCHEDULE_LOOKAHEAD = datetime.timedelta(days=7)

WAIT_MARKET_OPEN = True

ORDERS_CACHE_PATH = Path("close_cancelled_orders.json")

MSK = ZoneInfo("Europe/Moscow")
UTC = datetime.timezone.utc

EXPIRATION_TYPE = StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    with Client(TOKEN) as client:
        account_id = client.users.get_accounts().accounts[0].id

        if REPOST_MODE == "save":
            save_today_close_cancelled_orders(client, account_id)
            return

        orders = load_previous_trading_day_orders()

        if not orders:
            logger.info("No saved orders to repost")
            return

        logger.info("Loaded %s order(s) to repost", len(orders))

        if REPOST_MODE == "stop":
            for order in orders:
                repost_as_stop_order(client, account_id, order)
            return

        if REPOST_MODE == "limit_at_open":
            wait_market_open(client)
            for order in orders:
                repost_as_limit_order(client, account_id, order)
            return

        raise RuntimeError(f"Unsupported REPOST_MODE: {REPOST_MODE}")


def save_today_close_cancelled_orders(client: Services, account_id):
    from_, to = get_today_close_window()

    logger.info("Get cancelled orders from %s to %s", from_, to)

    response = client.orders.get_orders(
        GetOrdersRequest(
            account_id=account_id,
            advanced_filters=GetOrdersRequest.GetOrdersRequestFilters(
                from_=from_,
                to=to,
                execution_status=[
                    OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED
                ],
            ),
        )
    )

    orders = [
        order_to_cache_item(order)
        for order in response.orders
        if is_order_for_repost(order)
    ]

    cache = load_orders_cache()
    cache[get_today_key()] = orders
    save_orders_cache(cache)

    logger.info("Saved %s order(s)", len(orders))


def get_today_close_window():
    day = datetime.datetime.now(MSK).date()

    close_time = datetime.datetime.combine(
        day,
        MOEX_CLOSE_TIME,
        tzinfo=MSK,
    ).astimezone(UTC)

    return close_time - CLOSE_WINDOW, close_time


def load_previous_trading_day_orders():
    cache = load_orders_cache()
    day = get_previous_weekday()
    key = day.isoformat()

    logger.info("Load saved orders for %s", key)

    return cache.get(key, [])


def get_previous_weekday():
    day = datetime.datetime.now(MSK).date() - datetime.timedelta(days=1)

    while day.weekday() >= 5:
        day -= datetime.timedelta(days=1)

    return day


def get_today_key():
    return datetime.datetime.now(MSK).date().isoformat()


def wait_market_open(client: Services):
    trading_start = get_next_trading_start(client)

    logger.info("Next trading start: %s", trading_start)

    if now() >= trading_start:
        return

    if not WAIT_MARKET_OPEN:
        raise RuntimeError(f"Market is not open yet. Start time: {trading_start}")

    while now() < trading_start:
        seconds = min((trading_start - now()).total_seconds(), 60)
        logger.info("Wait market open, seconds left: %s", int(seconds))
        time.sleep(seconds)


def get_next_trading_start(client: Services):
    request_time = now()

    response = client.instruments.trading_schedules(
        TradingSchedulesRequest(
            exchange=EXCHANGE,
            from_=request_time,
            to=request_time + SCHEDULE_LOOKAHEAD,
        )
    )

    candidates = []

    for schedule in response.exchanges:
        for day in schedule.days:
            if day.is_trading_day and day.start_time > request_time:
                candidates.append(day.start_time)

    if not candidates:
        raise RuntimeError("Next trading start not found")

    return min(candidates)


def repost_as_stop_order(client: Services, account_id, order):
    price = get_cached_price(order)

    response = client.stop_orders.post_stop_order(
        PostStopOrderRequest(
            quantity=order["quantity"],
            price=price,
            stop_price=price,
            direction=get_stop_direction(order["direction"]),
            account_id=account_id,
            expiration_type=EXPIRATION_TYPE,
            stop_order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LIMIT,
            instrument_id=order["instrument_id"],
            exchange_order_type=ExchangeOrderType.EXCHANGE_ORDER_TYPE_LIMIT,
            order_id=str(uuid4()),
        )
    )

    logger.info("Stop order posted: %s", response)


def repost_as_limit_order(client: Services, account_id, order):
    response = client.orders.post_order(
        PostOrderRequest(
            quantity=order["quantity"],
            price=get_cached_price(order),
            direction=order["direction"],
            account_id=account_id,
            order_type=OrderType.ORDER_TYPE_LIMIT,
            instrument_id=order["instrument_id"],
            order_id=str(uuid4()),
        )
    )

    logger.info("Limit order posted: %s", response)


def is_order_for_repost(order):
    return (
        order.order_type == OrderType.ORDER_TYPE_LIMIT
        and order.direction
        in (
            OrderDirection.ORDER_DIRECTION_BUY,
            OrderDirection.ORDER_DIRECTION_SELL,
        )
        and (order.instrument_uid or order.figi)
        and (order.initial_security_price.units or order.initial_security_price.nano)
        and get_remaining_quantity(order) > 0
    )


def order_to_cache_item(order):
    price = order.initial_security_price

    return {
        "source_order_id": order.order_id,
        "instrument_id": order.instrument_uid or order.figi,
        "direction": order.direction,
        "quantity": get_remaining_quantity(order),
        "price": {
            "units": price.units,
            "nano": price.nano,
        },
    }


def get_remaining_quantity(order):
    return order.lots_requested - order.lots_executed


def get_cached_price(order):
    return Quotation(
        units=order["price"]["units"],
        nano=order["price"]["nano"],
    )


def get_stop_direction(direction):
    if direction == OrderDirection.ORDER_DIRECTION_BUY:
        return StopOrderDirection.STOP_ORDER_DIRECTION_BUY

    return StopOrderDirection.STOP_ORDER_DIRECTION_SELL


def load_orders_cache():
    if not ORDERS_CACHE_PATH.exists():
        return {}

    with ORDERS_CACHE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_orders_cache(cache):
    with ORDERS_CACHE_PATH.open("w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
