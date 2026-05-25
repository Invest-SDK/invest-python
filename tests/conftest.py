from unittest.mock import Mock

import pytest

from t_tech.invest.grpc.base_service import BaseService


@pytest.fixture
def patch_base_service_init(mocker):
    def fake_base_init(self, channel, metadata):
        self._metadata = metadata
        self._stub = Mock()

    mocker.patch.object(BaseService, "__init__", new=fake_base_init)
