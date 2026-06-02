from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from trillia_monitor.application.use_cases.get_rate_history import (
    MAX_HISTORY_DAYS,
    GetRateHistoryUseCase,
)
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.exceptions import InvalidDateRange
from trillia_monitor.domain.value_objects import CurrencyPair

from .fakes import InMemoryRateRepository


def _rate(day: int) -> ExchangeRate:
    ts = datetime(2026, 5, day, tzinfo=UTC)
    return ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5"),
        ask=Decimal("5.01"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )


@pytest.mark.asyncio
async def test_rejects_start_after_end() -> None:
    repo = InMemoryRateRepository()
    use_case = GetRateHistoryUseCase(repository=repo)
    start = datetime(2026, 5, 10, tzinfo=UTC)
    end = datetime(2026, 5, 1, tzinfo=UTC)
    with pytest.raises(InvalidDateRange):
        await use_case.execute(CurrencyPair("USD", "BRL"), start, end)


@pytest.mark.asyncio
async def test_rejects_range_larger_than_limit() -> None:
    repo = InMemoryRateRepository()
    use_case = GetRateHistoryUseCase(repository=repo)
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=MAX_HISTORY_DAYS + 1)
    with pytest.raises(InvalidDateRange):
        await use_case.execute(CurrencyPair("USD", "BRL"), start, end)


@pytest.mark.asyncio
async def test_returns_rates_within_range_inclusive() -> None:
    repo = InMemoryRateRepository()
    for d in (1, 5, 10, 15):
        await repo.save(_rate(d))
    use_case = GetRateHistoryUseCase(repository=repo)
    start = datetime(2026, 5, 5, tzinfo=UTC)
    end = datetime(2026, 5, 10, tzinfo=UTC)
    result = await use_case.execute(CurrencyPair("USD", "BRL"), start, end)
    assert [r.fetched_at.day for r in result] == [5, 10]


@pytest.mark.asyncio
async def test_empty_when_no_rates_match() -> None:
    repo = InMemoryRateRepository()
    use_case = GetRateHistoryUseCase(repository=repo)
    result = await use_case.execute(
        CurrencyPair("USD", "BRL"),
        datetime(2026, 5, 1, tzinfo=UTC),
        datetime(2026, 5, 31, tzinfo=UTC),
    )
    assert result == []
