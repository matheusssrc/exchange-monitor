from collections.abc import Sequence
from datetime import datetime

from trillia_monitor.application.ports.rate_provider import RateProvider
from trillia_monitor.application.ports.rate_repository import RateRepository
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair


class InMemoryRateRepository(RateRepository):
    def __init__(self, monitored: Sequence[CurrencyPair] = ()):
        self._rows: list[ExchangeRate] = []
        self._monitored = list(monitored)

    async def save(self, rate: ExchangeRate) -> None:
        self._rows.append(rate)

    async def get_latest(self, pair: CurrencyPair) -> ExchangeRate | None:
        matching = [r for r in self._rows if r.pair == pair]
        if not matching:
            return None
        return max(matching, key=lambda r: r.provider_timestamp)

    async def get_history(
        self,
        pair: CurrencyPair,
        start: datetime,
        end: datetime,
        limit: int = 1000,
        offset: int = 0,
    ) -> Sequence[ExchangeRate]:
        rows = [r for r in self._rows if r.pair == pair and start <= r.fetched_at <= end]
        rows.sort(key=lambda r: r.fetched_at)
        return rows[offset : offset + limit]

    async def list_monitored_pairs(self) -> Sequence[CurrencyPair]:
        return list(self._monitored)


class StubRateProvider(RateProvider):
    def __init__(self, rate_to_return: ExchangeRate | Exception):
        self._rate = rate_to_return
        self.calls: list[CurrencyPair] = []

    async def fetch(self, pair: CurrencyPair) -> ExchangeRate:
        self.calls.append(pair)
        if isinstance(self._rate, Exception):
            raise self._rate
        return self._rate
