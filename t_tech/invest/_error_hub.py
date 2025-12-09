import re

from grpc import StatusCode
from sentry_sdk.types import Event

from .exceptions import RequestError, AioRequestError
from .constants import PACKAGE_NAME

__all__ = (
    "init_error_hub",
    "async_init_error_hub"
)

BEARER_PATTERN = re.compile(r'Bearer\s+[a-zA-Z0-9\-_\.]+', re.IGNORECASE)


def sanitize_bearer_tokens(event, hint) -> Event | None:
    def _sanitize_value(value):
        if isinstance(value, str):
            return BEARER_PATTERN.sub("[***Filtered***]", value)
        elif isinstance(value, dict):
            return {k: _sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [_sanitize_value(item) for item in value]
        else:
            return value

    if "exc_info" in hint:
        exc_type, exc_value, traceback = hint["exc_info"]
        if exc_type == RequestError or exc_type == AioRequestError:
            status_code = exc_value.code
            if status_code == StatusCode.UNAVAILABLE:
                return _sanitize_value(event)

    return None


def init_error_hub(client):
    import sentry_sdk
    from sentry_sdk.integrations.grpc import GRPCIntegration
    from sentry_sdk.integrations.modules import ModulesIntegration

    # noinspection PyProtectedMember
    sentry_sdk.init(
        dsn="https://invest-piapi-errorhub@error-hub.tbank.ru/00000000",
        send_default_pii=False,
        integrations=[
            GRPCIntegration(),
        ],
        disabled_integrations=[ModulesIntegration()],
        before_send=sanitize_bearer_tokens,
        release=PACKAGE_NAME,
        environment=client._target,
        max_breadcrumbs=10,
        enable_logs=False,
    )


async def async_init_error_hub(client):
    init_error_hub(client)
