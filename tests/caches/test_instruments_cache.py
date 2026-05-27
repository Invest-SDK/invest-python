import uuid
from dataclasses import dataclass

import pytest

from t_tech.invest import _grpc_helpers
from t_tech.invest.caching.overrides import InstrumentCacheableMethods
from t_tech.invest.grpc import InstrumentIdType, InstrumentRequest
from t_tech.invest.grpc.utils.grpc_services import InstrumentsService, Services


@dataclass
class InstrumentResponse(_grpc_helpers.Message):
    uid: str
    figi: str
    ticker: str
    class_code: str
    position_uid: str


@pytest.fixture
def instrument_response():
    return InstrumentResponse(
        uid=uuid.uuid4().hex,
        figi=uuid.uuid4().hex,
        ticker=uuid.uuid4().hex,
        class_code=uuid.uuid4().hex,
        position_uid=uuid.uuid4().hex,
    )


@pytest.mark.usefixtures("patch_base_service_init")
class TestInstrumentsCache:
    @pytest.mark.parametrize("method_to_cache", InstrumentCacheableMethods)
    def test_cache(self, method_to_cache, mocker, instrument_response):
        mocked_instrument_method = mocker.patch.object(
            InstrumentsService, method_to_cache.value, return_value=instrument_response
        )
        mocked_instrument_method.__name__ = method_to_cache.value
        service = Services(None, "", instrument_methods_to_cache=(method_to_cache,))
        method_func = getattr(service.instruments, method_to_cache.value)

        for _ in range(2):
            method_func(
                InstrumentRequest(
                    id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID,
                    class_code=instrument_response.class_code,
                    id=instrument_response.uid,
                )
            )

        cache = getattr(service.instruments, "_instrument_call_cache", None)
        assert (
            mocked_instrument_method.call_count == 2
        ), f"Expected 2 calls, got {mocked_instrument_method.call_count}"
        assert cache is not None
