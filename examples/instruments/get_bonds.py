import os

from t_tech.invest.grpc import Client, InstrumentsRequest
from t_tech.invest.grpc.schemas import InstrumentExchangeType

TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        r = client.instruments.bonds(InstrumentsRequest(
            instrument_exchange=InstrumentExchangeType.INSTRUMENT_EXCHANGE_UNSPECIFIED)
        )
        for bond in r.instruments:
            print(bond)


if __name__ == "__main__":
    main()
