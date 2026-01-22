# Breaking changes
## 0.4.0
- We have implemented code generation to increase new version delivery velocity
  - This change required us to mark as deprecated the services that were used in older versions. These services
will not be supported in the future, and new functions will not be added.
  - To migrate to the new versions of services, you need to follow these steps:
    - Replace `from t_tech.invest` and `from t_tech.invest.services` imports with `from t_tech.invest.grpc`
    - Replace `from t_tech.invest.schemas` imports with `from t_tech.invest.grpc.schemas`
    - Pay attention to function parameters, they could be wrapped with `request` parameter.  
      For example, `client.orders.post_order` parameters were wrapped with `PostOrderRequest` class. Inner fields of 
      this class are the same as the old parameters.
      Here is the short list of frequently used function changes:
      - `client.orders.post_order` -> `client.orders.post_order(request=PostOrderRequest(...))` 
      - `client.orders.cancel_order` -> `client.orders.cancel_order(request=CancelOrderRequest(...))`
      - `client.orders.get_order_state` -> `client.orders.get_order_state(request=GetOrderStateRequest(...))`
      - `client.orders.get_orders` -> `client.orders.get_orders(request=GetOrdersRequest(...))`. 
        More detailed: `account_id` was moved to `request` parameter, while other parameters are 
        wrapped with `GetOrdersRequestFilters` class.
      - `client.operations.get_operations` -> `clients.operation.get_operations(request=OperationsRequest(...))` 
      - `client.operations.get_positions` -> `client.operations.get_positions(request=PositionsRequest(...))`
      - `client.operations.get_portfolio` -> `client.operations.get_portfolio(request=PortfolioRequest(...))`
      - The most part of `client.intruments` functions were wrapped with `request` parameter.
      - `client.operations_stream.portfolio_stream` -> `client.operations_stream.portfolio_stream(request=PortfolioStreamRequest(...))`
      - `client.operations_stream.positions_stream` -> `client.operations_stream.positions_stream(request=PositionsStreamRequest(...))`
      - `client.orders_stream.trade_stream` -> `client.orders_stream.trade_stream(request=TradeStreamRequest(...))`
      - Check the other functions not listed above.
- In Russian:
  В новой версии мы реализовали генерацию кода для ускорения выпуска новых версий.
  - Мы были вынуждены пометить как устаревшие те сервисы, которые использовались в старых версиях. Эти сервисы
больше не будут поддерживаться, новые методы добавляться не будут.
  - Для миграции на новые версии созданных сервисов необходимо выполнить следующие шаги:
    - Заменить импорты `from t_tech.invest` и `from t_tech.invest.services` на `from t_tech.invest.grpc`
    - Заменить импорты `from t_tech.invest.schemas` на `from t_tech.invest.grpc.schemas`
    - Обратить внимание на параметры функций, которые могут быть перемещены во враппер `request`.  
      Например, параметры `client.orders.post_order` обернуты в класс `PostOrderRequest`. Внутренние поля этого класса 
      имеют те же названия, что и старые параметры.  
      Ниже приведен краткий список часто используемых функций и их изменения:
      - `client.orders.post_order` -> `client.orders.post_order(request=PostOrderRequest(...))` 
      - `client.orders.cancel_order` -> `client.orders.cancel_order(request=CancelOrderRequest(...))`
      - `client.orders.get_order_state` -> `client.orders.get_order_state(request=GetOrderStateRequest(...))`
      - `client.orders.get_orders` -> `client.orders.get_orders(request=GetOrdersRequest(...))` 
         Более подробно об изменении: `account_id` был перемещен в параметр `request`, а остальные параметры обернуты в класс `GetOrdersRequestFilters`.
      - `client.operations.get_operations` -> `clients.operation.get_operations(request=OperationsRequest(...))` 
      - `client.operations.get_positions` -> `client.operations.get_positions(request=PositionsRequest(...))`
      - `client.operations.get_portfolio` -> `client.operations.get_portfolio(request=PortfolioRequest(...))`
      - Большая часть функций из модуля `client.intruments` была обернута параметром `request`.
      - `client.operations_stream.portfolio_stream` -> `client.operations_stream.portfolio_stream(request=PortfolioStreamRequest(...))`
      - `client.operations_stream.positions_stream` -> `client.operations_stream.positions_stream(request=PositionsStreamRequest(...))`
      - `client.orders_stream.trade_stream` -> `client.orders_stream.trade_stream(request=TradeStreamRequest(...))`
      - Также проверьте другие функции, не перечисленные выше.
## 0.3.0
- Package naming changed to `t_tech` with all corresponding subpackages
## 0.2.0-beta60
- `MarketDataCache` was moved to [t_tech/invest/caching/market_data_cache/cache.py](t_tech/invest/caching/market_data_cache/cache.py).
- The correct import is now `from t_tech.invest.caching.market_data_cache.cache import MarketDataCache` instead of `from t_tech.invest.services import MarketDataCache`.
- Import in [download_all_candles.py](examples/download_all_candles.py) was also corrected.