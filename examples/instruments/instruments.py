import os

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import FindInstrumentRequest

TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        r = client.instruments.find_instrument(
            FindInstrumentRequest(query="BBG016CSVY38")
        )
        for i in r.instruments:
            print(i)


if __name__ == "__main__":
    main()
