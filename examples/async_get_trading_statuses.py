import asyncio
import os

from t_tech.invest.grpc import AsyncClient
from t_tech.invest.grpc.schemas import GetTradingStatusesRequest

token = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(token) as client:
        statuses = await client.market_data.get_trading_statuses(
            GetTradingStatusesRequest(instrument_id=["BBG004730N88"])
        )
        print(statuses)


if __name__ == "__main__":
    asyncio.run(main())
