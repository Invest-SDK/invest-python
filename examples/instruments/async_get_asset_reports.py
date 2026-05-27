import asyncio
import os
from datetime import timedelta

from t_tech.invest.grpc import AsyncClient
from t_tech.invest.grpc.schemas import (
    FindInstrumentRequest,
    GetAssetReportsRequest,
    InstrumentType,
)
from t_tech.invest.utils import now

TOKEN = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(TOKEN) as client:
        instruments = await client.instruments.find_instrument(
            FindInstrumentRequest(
                query="Южуралзолото",
                instrument_kind=InstrumentType.INSTRUMENT_TYPE_SHARE,
            )
        )
        instrument = instruments.instruments[0]
        print(instrument.name)
        request = GetAssetReportsRequest(
            instrument_id=instrument.uid,
            from_=now() - timedelta(days=7),
            to=now(),
        )
        print(await client.instruments.get_asset_reports(request=request))


if __name__ == "__main__":
    asyncio.run(main())
