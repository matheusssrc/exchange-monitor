from datetime import UTC, datetime
from decimal import Decimal

import pytest

from trillia_monitor.application.use_cases.get_latest_rate import GetLatestRateUseCase
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair

from .fakes import InMemoryRateRepository


def _rate(hour: int) -> ExchangeRate:
    ts = datetime(2026, 5, 27, hour, tzinfo=UTC)
    return ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5"),
        ask=Decimal("5.01"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )


@pytest.mark.asyncio
async def test_returns_none_when_no_rates_persisted() -> None:
    repo = InMemoryRateRepository()
    use_case = GetLatestRateUseCase(repository=repo)
    assert await use_case.execute(CurrencyPair("USD", "BRL")) is None


@pytest.mark.asyncio
async def test_returns_most_recent_rate_by_provider_timestamp() -> None:
    repo = InMemoryRateRepository()
    older = _rate(10)
    newer = _rate(12)
    await repo.save(older)
    await repo.save(newer)
    use_case = GetLatestRateUseCase(repository=repo)
    assert await use_case.execute(CurrencyPair("USD", "BRL")) == newer
