from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime

from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair


class RateRepository(ABC):
    @abstractmethod
    async def save(self, rate: ExchangeRate) -> None: ...

    @abstractmethod
    async def get_latest(self, pair: CurrencyPair) -> ExchangeRate | None: ...

    @abstractmethod
    async def get_history(
        self,
        pair: CurrencyPair,
        start: datetime,
        end: datetime,
        limit: int = 1000,
        offset: int = 0,
    ) -> Sequence[ExchangeRate]: ...

    @abstractmethod
    async def list_monitored_pairs(self) -> Sequence[CurrencyPair]: ...
