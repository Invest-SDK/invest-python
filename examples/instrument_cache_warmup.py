import logging
import os
from pprint import pprint

from t_tech.invest.caching.overrides import InstrumentCacheableMethodsToWarmup
from t_tech.invest.grpc import Client
from t_tech.invest.grpc.schemas import InstrumentIdType, InstrumentRequest

TOKEN = os.environ["INVEST_TOKEN"]


logging.basicConfig(level=logging.INFO)


def main():
    with Client(
        TOKEN, warmup_cache_methods=(InstrumentCacheableMethodsToWarmup.ETFS,)
    ) as client:
        inst = client.instruments.etfs().instruments[-1]
        pprint(inst)

        from_cache = client.instruments.etf_by(
            request=InstrumentRequest(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID,
                class_code=inst.class_code,
                id=inst.uid,
            )
        )
        pprint(from_cache)


if __name__ == "__main__":
    main()
