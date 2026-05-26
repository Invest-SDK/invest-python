import os

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import InstrumentsRequest, InstrumentStatus


def main():
    token = os.environ["INVEST_TOKEN"]

    with Client(token) as client:
        r = client.instruments.structured_notes(
            request=InstrumentsRequest(
                instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL
            )
        )
        for note in r.instruments:
            print(note)


if __name__ == "__main__":
    main()
