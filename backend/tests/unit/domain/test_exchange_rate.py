from datetime import UTC, datetime
from decimal import Decimal

import pytest

from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair


def _utc(year: int = 2026, month: int = 5, day: int = 27, hour: int = 12) -> datetime:
    return datetime(year, month, day, hour, tzinfo=UTC)


def _rate(**overrides: object) -> ExchangeRate:
    defaults: dict[str, object] = dict(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5.1200"),
        ask=Decimal("5.1210"),
        fetched_at=_utc(),
        provider_timestamp=_utc(hour=11),
        provider_name="awesomeapi",
    )
    defaults.update(overrides)
    return ExchangeRate(**defaults)  # type: ignore[arg-type]


class TestExchangeRateInvariants:
    def test_constructs_with_valid_values(self) -> None:
        rate = _rate()
        assert rate.bid == Decimal("5.1200")
        assert rate.ask == Decimal("5.1210")

    @pytest.mark.parametrize(
        "bid,ask",
        [
            (Decimal("0"), Decimal("5")),
            (Decimal("-1"), Decimal("5")),
            (Decimal("5"), Decimal("0")),
            (Decimal("5"), Decimal("-1")),
        ],
    )
    def test_rejects_non_positive_rates(self, bid: Decimal, ask: Decimal) -> None:
        with pytest.raises(ValueError, match="positive"):
            _rate(bid=bid, ask=ask)

    def test_rejects_ask_smaller_than_bid(self) -> None:
        with pytest.raises(ValueError, match=">= bid"):
            _rate(bid=Decimal("5.13"), ask=Decimal("5.12"))

    def test_allows_ask_equal_to_bid(self) -> None:
        rate = _rate(bid=Decimal("5.12"), ask=Decimal("5.12"))
        assert rate.bid == rate.ask

    def test_rejects_naive_fetched_at(self) -> None:
        with pytest.raises(ValueError, match="timezone-aware"):
            _rate(fetched_at=datetime(2026, 5, 27, 12))

    def test_rejects_naive_provider_timestamp(self) -> None:
        with pytest.raises(ValueError, match="timezone-aware"):
            _rate(provider_timestamp=datetime(2026, 5, 27, 11))


class TestExchangeRateMid:
    def test_mid_is_average_of_bid_and_ask(self) -> None:
        rate = _rate(bid=Decimal("5.1200"), ask=Decimal("5.1210"))
        assert rate.mid == Decimal("5.1205")
