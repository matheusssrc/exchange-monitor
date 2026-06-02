from abc import ABC, abstractmethod

from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair


class RateProvider(ABC):
    @abstractmethod
    async def fetch(self, pair: CurrencyPair) -> ExchangeRate: ...
