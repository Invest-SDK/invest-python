# Карта T-Invest Python SDK

## Актуальные импорты

Используйте gRPC-интерфейс:

```python
from t_tech.invest.grpc import AsyncClient, AsyncSandboxClient
from t_tech.invest.grpc import Client, SandboxClient
from t_tech.invest.grpc.schemas import GetAccountsRequest
```

Импорты `tinkoff.invest` устарели. Старые сервисы из
`t_tech.invest.services` не следует использовать в новом коде.

## Клиенты

| Клиент | Выполнение | Контур |
|---|---|---|
| `Client` | синхронное | реальный по умолчанию |
| `AsyncClient` | асинхронное | реальный по умолчанию |
| `SandboxClient` | синхронное | песочница |
| `AsyncSandboxClient` | асинхронное | песочница |

Контекстный менеджер возвращает набор сервисов:

```python
import os

from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import GetAccountsRequest


token = os.environ["INVEST_TOKEN"]

with Client(token) as services:
    response = services.users.get_accounts(request=GetAccountsRequest())
    print(response.accounts)
```

Асинхронный вариант требует `async with` и `await`:

```python
import asyncio
import os

from t_tech.invest.grpc import AsyncClient
from t_tech.invest.grpc.schemas import GetAccountsRequest


async def main() -> None:
    token = os.environ["INVEST_TOKEN"]
    async with AsyncClient(token) as services:
        response = await services.users.get_accounts(
            request=GetAccountsRequest()
        )
        print(response.accounts)


asyncio.run(main())
```

## Основные сервисы

| Атрибут | Назначение |
|---|---|
| `services.users` | счета и пользовательские параметры |
| `services.instruments` | поиск инструментов и их свойства |
| `services.market_data` | свечи, цены, стаканы и торговые статусы |
| `services.market_data_stream` | поток рыночных данных |
| `services.operations` | портфель, позиции и операции |
| `services.operations_stream` | поток изменений портфеля и позиций |
| `services.orders` | обычные биржевые заявки |
| `services.orders_stream` | поток состояния заявок и сделок |
| `services.stop_orders` | стоп-заявки |
| `services.sandbox` | специальные операции песочницы |
| `services.signals` | сигнальные методы API |

Точный состав сервисов находится в
`t_tech/invest/grpc/utils/grpc_services.py`.

## Request-модели

Большинство gRPC-методов принимает объект запроса:

```python
response = services.some_service.some_method(
    request=SomeMethodRequest(
        # Поля из определения модели текущей версии.
    )
)
```

Перед генерацией вызова найдите метод и request-класс:

```bash
rg -n "def some_method|class SomeMethodRequest" t_tech/invest/grpc
```

Не переносите keyword-аргументы из старых примеров автоматически: после
перехода на gRPC часть аргументов была перемещена внутрь request-моделей.

## Финансовые преобразования

Публичные функции преобразования находятся в `t_tech.invest.utils`:

```python
from t_tech.invest.utils import decimal_to_money, decimal_to_quotation
from t_tech.invest.utils import money_to_decimal, quotation_to_decimal
```

- `quotation_to_decimal` и `decimal_to_quotation` преобразуют `Quotation`;
- `money_to_decimal` и `decimal_to_money` преобразуют `MoneyValue`, причём
  `decimal_to_money` также принимает код валюты.

Используйте их на границе API. Не собирайте `units` и `nano` вручную и не
применяйте `float` в расчётах денег или цены заявки.

## Идентификаторы заявки

В текущем контракте похожие имена имеют разный смысл:

- `PostOrderRequest.order_id` — созданный клиентом ключ идемпотентности;
- `PostOrderResponse.order_id` — биржевой идентификатор заявки;
- `PostOrderResponse.order_request_id` — возвращённый клиентский ключ
  идемпотентности.

Сохраняйте клиентский ключ до сетевого вызова и не смешивайте его с биржевым
идентификатором. `GetOrderStateRequest` принимает `order_id` и опциональный
`order_id_type`: для клиентского ключа используйте
`OrderIdType.ORDER_ID_TYPE_REQUEST`, а для биржевого —
`OrderIdType.ORDER_ID_TYPE_EXCHANGE`. Перед генерацией вызова всё равно
сверьте поля и enum с текущей версией моделей.

## Где проверять типы

- агрегированные модели: `t_tech/invest/grpc/schemas.py`;
- заявки: `t_tech/invest/grpc/orders.py`;
- рыночные данные: `t_tech/invest/grpc/marketdata.py`;
- инструменты: `t_tech/invest/grpc/instruments.py`;
- портфель и операции: `t_tech/invest/grpc/operations.py`;
- песочница: `t_tech/invest/grpc/sandbox.py`;
- исходный контракт: `protos/t_tech/invest/grpc/`.

Сгенерированные сигнатуры текущей версии являются более надёжным источником,
чем пример из другой версии SDK.
