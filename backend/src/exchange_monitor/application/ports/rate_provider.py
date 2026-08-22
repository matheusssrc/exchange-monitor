from abc import ABC, abstractmethod

from exchange_monitor.domain.entities import ExchangeRate
from exchange_monitor.domain.value_objects import CurrencyPair


class RateProvider(ABC):
    @abstractmethod
    async def fetch(self, pair: CurrencyPair) -> ExchangeRate: ...
