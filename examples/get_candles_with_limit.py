import os

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import CandleInterval, GetCandlesRequest
from t_tech.invest.utils import now

TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        for candle in client.market_data.get_candles(
            GetCandlesRequest(
                instrument_id="BBG004730N88",
                to=now(),
                limit=24,
                interval=CandleInterval.CANDLE_INTERVAL_HOUR,
            )
        ).candles:
            print(candle)

    return 0


if __name__ == "__main__":
    main()
