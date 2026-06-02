from dataclasses import dataclass

from trillia_monitor.application.ports.rate_repository import RateRepository
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair


@dataclass
class GetLatestRateUseCase:
    repository: RateRepository

    async def execute(self, pair: CurrencyPair) -> ExchangeRate | None:
        return await self.repository.get_latest(pair)
