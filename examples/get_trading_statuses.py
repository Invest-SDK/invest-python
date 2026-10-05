import os

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import GetTradingStatusesRequest

token = os.environ["INVEST_TOKEN"]


with Client(token) as client:
    statuses = client.market_data.get_trading_statuses(
        GetTradingStatusesRequest(instrument_id=["BBG004730N88"])
    )
    print(statuses)
