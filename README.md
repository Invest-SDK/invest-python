# T-Invest

[![PyPI](https://img.shields.io/pypi/v/t-tech-investments)](https://pypi.org/project/t-tech-investments/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/t-tech-investments)](https://www.python.org/downloads/)
[![Opensource](https://img.shields.io/pypi/l/t-tech-investments)](https://opensource.tbank.ru/invest/invest-python/-/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dw/t-tech-investments)

Данный репозиторий предоставляет клиент для взаимодействия с торговой платформой [Т-Инвестиции](https://www.tbank.ru/invest/) на языке Python.

- [Документация](https://opensource.tbank.ru/invest/invest-python/-/blob/master/README.md?ref_type=heads)
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

Остальные примеры доступны в [examples](https://opensource.tbank.ru/invest/invest-python/-/tree/master/examples).

## Contribution

Для тех, кто хочет внести свои изменения в проект.

- [CONTRIBUTING](https://opensource.tbank.ru/invest/invest-python/-/blob/master/CONTRIBUTING.md)

## License

Лицензия [The Apache License](https://opensource.tbank.ru/invest/invest-python/-/blob/master/LICENSE).
