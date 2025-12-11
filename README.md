# T-Invest

[//]: # ([![PyPI]&#40;https://img.shields.io/pypi/v/t-tech-investments&#41;]&#40;https://pypi.org/project/t-tech-investments/&#41;)
[//]: # (#[![PyPI - Python Version]&#40;https://img.shields.io/pypi/pyversions/t-tech-investments&#41;]&#40;https://www.python.org/downloads/&#41;)
[//]: # (#![GitHub]&#40;https://img.shields.io/github/license/tinkoff/invest-python&#41;)
[//]: # (#![PyPI - Downloads]&#40;https://img.shields.io/pypi/dm/t-tech-investments&#41;)

Данный репозиторий предоставляет клиент для взаимодействия с торговой платформой [Т-Инвестиции](https://www.tbank.ru/invest/) на языке Python.

- [Документация](https://RussianInvestments.github.io/invest-python/)
- [Документация по Invest API](https://developer.tbank.ru/invest/intro/intro)

## Начало работы

<!-- termynal -->

```
$ pip install t-tech-investments
```

## Возможности

- &#9745; Синхронный и асинхронный GRPC клиент
- &#9745; Возможность отменить все заявки
- &#9745; Выгрузка истории котировок "от" и "до"
- &#9745; Кеширование данных
- &#9745; Торговая стратегия

## Как пользоваться

### Получить список аккаунтов

```python
from t_tech.invest import Client

TOKEN = 'token'

with Client(TOKEN) as client:
    print(client.users.get_accounts())
```

### Переопределить target

В T-Invest API есть два контура - "боевой", предназначенный для исполнения ордеров на бирже и "песочница", предназначенный для тестирования API и торговых гипотез, заявки с которого не выводятся на биржу, а исполняются в эмуляторе.

Переключение между контурами реализовано через target, INVEST_GRPC_API - "боевой", INVEST_GRPC_API_SANDBOX - "песочница"

```python
from t_tech.invest import Client
from t_tech.invest.constants import INVEST_GRPC_API

TOKEN = 'token'

with Client(TOKEN, target=INVEST_GRPC_API) as client:
    print(client.users.get_accounts())
```

> :warning: **Не публикуйте токены в общедоступные репозитории**
<br/>

Остальные примеры доступны в [examples](https://opensource.tbank.ru/invest/invest-python/-/tree/main/examples).

## Contribution

Для тех, кто хочет внести свои изменения в проект.

- [CONTRIBUTING](https://opensource.tbank.ru/invest/invest-python/-/blob/main/CONTRIBUTING.md)

## License

Лицензия [The Apache License](https://opensource.tbank.ru/invest/invest-python/-/blob/main/LICENSE).
