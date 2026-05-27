import asyncio
import os

from t_tech.invest.grpc import AsyncClient
from t_tech.invest.grpc.schemas import (
    FindInstrumentRequest,
    GetBondEventsRequest,
    InstrumentType,
)

TOKEN = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(TOKEN) as client:
        bond = (
            await client.instruments.find_instrument(
                FindInstrumentRequest(
                    query="Т-Банк TCS-perp2",
                    instrument_kind=InstrumentType.INSTRUMENT_TYPE_BOND,
                )
            )
        ).instruments[0]

        request = GetBondEventsRequest(
            instrument_id=bond.uid,
            type=GetBondEventsRequest.EventType.EVENT_TYPE_CALL,
        )
        print(await client.instruments.get_bond_events(request=request))


if __name__ == "__main__":
    asyncio.run(main())
