from datetime import UTC, datetime
from decimal import Decimal

import pytest

from trillia_monitor.application.use_cases.collect_rate import CollectRateUseCase
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair

from .fakes import InMemoryRateRepository, StubRateProvider


def _utc(hour: int = 12) -> datetime:
    return datetime(2026, 5, 27, hour, tzinfo=UTC)


@pytest.mark.asyncio
async def test_collect_persists_rate_returned_by_provider() -> None:
    pair = CurrencyPair("USD", "BRL")
    rate = ExchangeRate(
        pair=pair,
        bid=Decimal("5.12"),
        ask=Decimal("5.13"),
        fetched_at=_utc(),
        provider_timestamp=_utc(11),
        provider_name="awesomeapi",
    )
    provider = StubRateProvider(rate)
    repo = InMemoryRateRepository()
    use_case = CollectRateUseCase(provider=provider, repository=repo)

    await use_case.execute(pair)

    stored = await repo.get_latest(pair)
    assert stored == rate
    assert provider.calls == [pair]


@pytest.mark.asyncio
async def test_collect_propagates_provider_failure() -> None:
    pair = CurrencyPair("USD", "BRL")
    provider = StubRateProvider(RuntimeError("boom"))
    repo = InMemoryRateRepository()
    use_case = CollectRateUseCase(provider=provider, repository=repo)

    with pytest.raises(RuntimeError, match="boom"):
        await use_case.execute(pair)

    assert await repo.get_latest(pair) is None
