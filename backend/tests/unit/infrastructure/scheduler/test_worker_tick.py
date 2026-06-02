from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock

import pytest

from tests.unit.application.use_cases.fakes import InMemoryRateRepository
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.providers.exceptions import ProviderUnavailable
from trillia_monitor.infrastructure.scheduler.worker import _tick


class _FakeSessionCM:
    def __init__(self, sentinel: object) -> None:
        self.sentinel = sentinel

    async def __aenter__(self) -> object:
        return self.sentinel

    async def __aexit__(self, *exc: object) -> bool:
        return False


def _make_session_factory() -> Any:
    sentinel = object()
    return lambda: _FakeSessionCM(sentinel)


def _rate() -> ExchangeRate:
    ts = datetime(2026, 5, 27, tzinfo=UTC)
    return ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5.12"),
        ask=Decimal("5.13"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )


@pytest.mark.asyncio
async def test_tick_invokes_collect_use_case(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tick wires the use case to the in-memory repo and saves the rate."""
    repo = InMemoryRateRepository(monitored=[CurrencyPair("USD", "BRL")])

    import trillia_monitor.infrastructure.scheduler.worker as w

    monkeypatch.setattr(w, "SqlAlchemyRateRepository", lambda **_: repo)

    provider = AsyncMock()
    provider.fetch.return_value = _rate()

    await _tick(
        pair=CurrencyPair("USD", "BRL"),
        provider=provider,
        session_factory=_make_session_factory(),
        monitored_pairs=[CurrencyPair("USD", "BRL")],
    )
    latest = await repo.get_latest(CurrencyPair("USD", "BRL"))
    assert latest is not None


@pytest.mark.asyncio
async def test_tick_swallows_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import trillia_monitor.infrastructure.scheduler.worker as w

    repo = InMemoryRateRepository(monitored=[CurrencyPair("USD", "BRL")])
    monkeypatch.setattr(w, "SqlAlchemyRateRepository", lambda **_: repo)

    provider = AsyncMock()
    provider.fetch.side_effect = ProviderUnavailable("boom")

    await _tick(
        pair=CurrencyPair("USD", "BRL"),
        provider=provider,
        session_factory=_make_session_factory(),
        monitored_pairs=[CurrencyPair("USD", "BRL")],
    )
    assert await repo.get_latest(CurrencyPair("USD", "BRL")) is None
