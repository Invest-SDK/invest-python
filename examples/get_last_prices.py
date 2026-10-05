import os

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import GetLastPricesRequest, InstrumentStatus

TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        print(
            client.market_data.get_last_prices(
                GetLastPricesRequest(
                    figi=["BBG004730ZJ9"],
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE,
                )
            )
        )


if __name__ == "__main__":
    main()
