from datetime import UTC, datetime
from decimal import Decimal

from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.persistence.mappers import to_domain, to_orm
from trillia_monitor.infrastructure.persistence.models import ExchangeRateModel


def _rate() -> ExchangeRate:
    ts = datetime(2026, 5, 27, 12, tzinfo=UTC)
    return ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5.1200"),
        ask=Decimal("5.1210"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )


def test_to_orm_copies_fields() -> None:
    rate = _rate()
    orm = to_orm(rate)
    assert isinstance(orm, ExchangeRateModel)
    assert orm.pair == "USD-BRL"
    assert orm.bid == Decimal("5.1200")
    assert orm.ask == Decimal("5.1210")
    assert orm.fetched_at == rate.fetched_at
    assert orm.provider_timestamp == rate.provider_timestamp
    assert orm.provider_name == "awesomeapi"


def test_to_domain_reconstructs_entity() -> None:
    rate = _rate()
    orm = to_orm(rate)
    restored = to_domain(orm)
    assert restored == rate


def test_round_trip_preserves_decimal_precision() -> None:
    rate = _rate()
    restored = to_domain(to_orm(rate))
    assert isinstance(restored.bid, Decimal)
    assert isinstance(restored.ask, Decimal)
