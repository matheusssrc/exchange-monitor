from dataclasses import dataclass

import structlog

from exchange_monitor.application.ports.rate_provider import RateProvider
from exchange_monitor.application.ports.rate_repository import RateRepository
from exchange_monitor.domain.value_objects import CurrencyPair

log = structlog.get_logger()


@dataclass
class CollectRateUseCase:
    provider: RateProvider
    repository: RateRepository

    async def execute(self, pair: CurrencyPair) -> None:
        log.info("rate.collect.start", pair=str(pair))
        rate = await self.provider.fetch(pair)
        await self.repository.save(rate)
        log.info(
            "rate.collect.saved",
            pair=str(pair),
            bid=str(rate.bid),
            ask=str(rate.ask),
        )
