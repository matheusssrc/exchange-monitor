from collections.abc import Sequence
from dataclasses import dataclass

from trillia_monitor.application.ports.rate_repository import RateRepository
from trillia_monitor.domain.value_objects import CurrencyPair


@dataclass
class ListPairsUseCase:
    repository: RateRepository

    async def execute(self) -> Sequence[CurrencyPair]:
        return await self.repository.list_monitored_pairs()
