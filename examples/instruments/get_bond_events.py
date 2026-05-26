import os

from t_tech.invest.grpc import Client, FindInstrumentRequest
from t_tech.invest.grpc.schemas import GetBondEventsRequest, InstrumentType

TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        bond = client.instruments.find_instrument(
            FindInstrumentRequest(
                query="Т-Банк TCS-perp2",
                instrument_kind=InstrumentType.INSTRUMENT_TYPE_BOND,
            )
        ).instruments[0]

        request = GetBondEventsRequest(
            instrument_id=bond.uid,
            type=GetBondEventsRequest.EventType.EVENT_TYPE_CALL,
        )
        print(client.instruments.get_bond_events(request=request))


if __name__ == "__main__":
    main()
