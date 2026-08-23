from dataclasses import dataclass

from exchange_monitor.application.ports.rate_repository import RateRepository
from exchange_monitor.domain.entities import ExchangeRate
from exchange_monitor.domain.value_objects import CurrencyPair


@dataclass
class GetLatestRateUseCase:
    repository: RateRepository

    async def execute(self, pair: CurrencyPair) -> ExchangeRate | None:
        return await self.repository.get_latest(pair)
