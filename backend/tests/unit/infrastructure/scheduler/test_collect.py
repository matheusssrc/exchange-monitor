from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock

import pytest

from tests.unit.application.use_cases.fakes import InMemoryRateRepository
from trillia_monitor.config import Settings
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.providers.exceptions import ProviderUnavailable
from trillia_monitor.infrastructure.scheduler import collect as collect_module
from trillia_monitor.infrastructure.scheduler.collect import collect_pair


class _FakeSessionCM:
    def __init__(self, sentinel: object) -> None:
        self.sentinel = sentinel

    async def __aenter__(self) -> object:
        return self.sentinel

    async def __aexit__(self, *exc: object) -> bool:
        return False


def _settings() -> Settings:
    return Settings(_env_file=None, monitored_pairs=[CurrencyPair("USD", "BRL")])  # type: ignore[call-arg]


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


@pytest.fixture
def _patched(monkeypatch: pytest.MonkeyPatch) -> InMemoryRateRepository:
    repo = InMemoryRateRepository(monitored=[CurrencyPair("USD", "BRL")])
    sentinel = object()

    monkeypatch.setattr(collect_module, "build_engine", lambda _url: object())
    monkeypatch.setattr(
        collect_module, "build_session_factory", lambda _engine: lambda: _FakeSessionCM(sentinel)
    )
    monkeypatch.setattr(collect_module, "SqlAlchemyRateRepository", lambda **_: repo)

    async def _noop_dispose(_engine: object) -> None:
        return None

    monkeypatch.setattr(collect_module, "_dispose_engine", _noop_dispose)
    return repo


def _stub_provider(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Patch _build_provider to return (provider, client) of AsyncMocks."""
    provider = AsyncMock()
    client = AsyncMock()
    client.aclose = AsyncMock()
    monkeypatch.setattr(collect_module, "_build_provider", lambda _settings: (provider, client))
    return provider


def test_collect_pair_persists_rate(
    _patched: InMemoryRateRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = _stub_provider(monkeypatch)
    provider.fetch.return_value = _rate()

    collect_pair("USD-BRL", settings=_settings())

    stored: Any = _patched._rows
    assert len(stored) == 1


def test_collect_pair_swallows_provider_error(
    _patched: InMemoryRateRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = _stub_provider(monkeypatch)
    provider.fetch.side_effect = ProviderUnavailable("boom")

    # Must NOT raise — failures are logged + counted, never crash the task.
    collect_pair("USD-BRL", settings=_settings())
    assert _patched._rows == []
