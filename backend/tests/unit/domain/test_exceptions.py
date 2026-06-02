import pytest

from trillia_monitor.domain.exceptions import (
    DomainError,
    InvalidCurrencyPair,
    InvalidDateRange,
    RateNotFound,
)


@pytest.mark.parametrize("cls", [InvalidCurrencyPair, InvalidDateRange, RateNotFound])
def test_exceptions_inherit_from_domain_error(cls: type[Exception]) -> None:
    assert issubclass(cls, DomainError)


def test_domain_error_is_exception_subclass() -> None:
    assert issubclass(DomainError, Exception)
