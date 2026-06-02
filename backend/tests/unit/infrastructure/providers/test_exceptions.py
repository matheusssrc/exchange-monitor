import pytest

from trillia_monitor.infrastructure.providers.exceptions import (
    ProviderError,
    ProviderRateLimited,
    ProviderResponseInvalid,
    ProviderUnavailable,
)


@pytest.mark.parametrize(
    "cls",
    [ProviderRateLimited, ProviderResponseInvalid, ProviderUnavailable],
)
def test_subclasses_inherit_from_provider_error(cls: type[Exception]) -> None:
    assert issubclass(cls, ProviderError)


def test_provider_error_is_exception() -> None:
    assert issubclass(ProviderError, Exception)
