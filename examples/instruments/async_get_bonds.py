import asyncio
import os

from t_tech.invest.grpc import AsyncClient, InstrumentsRequest
from t_tech.invest.grpc.schemas import InstrumentExchangeType

TOKEN = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(TOKEN) as client:
        bonds = await client.instruments.bonds(
            InstrumentsRequest(
                instrument_exchange=InstrumentExchangeType.INSTRUMENT_EXCHANGE_UNSPECIFIED,
            )
        )
        for bond in bonds.instruments:
            print(bond)


if __name__ == "__main__":
    asyncio.run(main())
