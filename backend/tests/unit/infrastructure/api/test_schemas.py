from datetime import UTC, datetime
from decimal import Decimal

from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.api.schemas import (
    ErrorOut,
    HistoryPage,
    PairOut,
    RateOut,
)


def test_rate_out_from_domain_serialises_decimal_as_string() -> None:
    ts = datetime(2026, 5, 27, 12, tzinfo=UTC)
    rate = ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5.1200"),
        ask=Decimal("5.1210"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )
    dto = RateOut.from_domain(rate)
    payload = dto.model_dump(mode="json")
    assert payload["pair"] == "USD-BRL"
    assert payload["bid"] == "5.1200"
    assert payload["mid"] == "5.1205"


def test_history_page_serialises_items() -> None:
    ts = datetime(2026, 5, 27, tzinfo=UTC)
    rate = ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5"),
        ask=Decimal("5.1"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )
    page = HistoryPage(
        pair="USD-BRL",
        start=ts,
        end=ts,
        count=1,
        items=[RateOut.from_domain(rate)],
    )
    assert page.count == 1
    assert page.items[0].pair == "USD-BRL"


def test_pair_out_holds_components() -> None:
    out = PairOut(pair="USD-BRL", base="USD", quote="BRL")
    assert out.base == "USD"
    assert out.quote == "BRL"


def test_error_out_contains_required_fields() -> None:
    err = ErrorOut(error="not_found", message="missing")
    assert err.error == "not_found"
    assert err.message == "missing"
