import asyncio
import os

from t_tech.invest.grpc import AsyncClient
from t_tech.invest.grpc.schemas import NewsRequest

TOKEN = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(TOKEN) as client:
        # получаем список новостей
        news_response = await client.instruments.news(NewsRequest(limit=10))
        news = news_response.items

        if news_response.has_next:
            # дополняем список блоком новостей, начиная с того места, где остановились
            news_response = await client.instruments.news(
                NewsRequest(limit=10, cursor=news_response.next_cursor)
            )
            news += news_response.items

        for n in news:
            print(n)


if __name__ == "__main__":
    asyncio.run(main())
