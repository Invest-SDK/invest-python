import logging
import os
from pprint import pprint

from t_tech.invest.caching.overrides import InstrumentCacheableMethods
from t_tech.invest.grpc import Client
from t_tech.invest.grpc.instruments import InstrumentIdType, InstrumentRequest

TOKEN = os.environ["INVEST_TOKEN"]


logging.basicConfig(level=logging.INFO)


def main():
    with Client(
        TOKEN, instrument_methods_to_cache=(InstrumentCacheableMethods.ETF_BY,)
    ) as client:
        inst = client.instruments.etfs().instruments[-1]
        pprint(inst)

        from_server = client.instruments.etf_by(
            request=InstrumentRequest(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID,
                class_code=inst.class_code,
                id=inst.uid,
            )
        )
        pprint(from_server)

        from_cache = client.instruments.etf_by(
            request=InstrumentRequest(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID,
                class_code=inst.class_code,
                id=inst.uid,
            )
        )
        pprint(from_cache)

        if str(from_server) != str(from_cache):
            raise Exception("cache miss")


if __name__ == "__main__":
    main()
