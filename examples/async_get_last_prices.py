import asyncio
import os

from t_tech.invest.grpc import AsyncClient
from t_tech.invest.grpc.schemas import GetLastPricesRequest, InstrumentStatus

TOKEN = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(TOKEN) as client:
        print(
            await client.market_data.get_last_prices(
                GetLastPricesRequest(
                    figi=["BBG004730ZJ9"],
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL,
                )
            )
        )  # pylint:disable=line-too-long


if __name__ == "__main__":
    asyncio.run(main())
