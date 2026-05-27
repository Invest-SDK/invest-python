import os

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import GetLastTradesRequest, TradeSourceType

TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        print(
            client.market_data.get_last_trades(
                GetLastTradesRequest(
                    instrument_id="BBG004730ZJ9",
                    trade_source=TradeSourceType.TRADE_SOURCE_EXCHANGE,
                )
            )
        )


if __name__ == "__main__":
    main()
