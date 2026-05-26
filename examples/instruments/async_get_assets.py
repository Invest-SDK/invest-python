import asyncio
import os

from t_tech.invest.grpc import AsyncClient
from t_tech.invest.grpc.schemas import AssetsRequest, InstrumentStatus, InstrumentType

TOKEN = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(TOKEN) as client:
        r = await client.instruments.get_assets(
            request=AssetsRequest(
                instrument_type=InstrumentType.INSTRUMENT_TYPE_SHARE,
                instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE,
            )
        )
        print("BASE SHARE ASSETS")
        for bond in r.assets:
            print(bond)


if __name__ == "__main__":
    asyncio.run(main())
