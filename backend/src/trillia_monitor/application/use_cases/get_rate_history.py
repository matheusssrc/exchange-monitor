from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from trillia_monitor.application.ports.rate_repository import RateRepository
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.exceptions import InvalidDateRange
from trillia_monitor.domain.value_objects import CurrencyPair

MAX_HISTORY_DAYS = 90


@dataclass
class GetRateHistoryUseCase:
    repository: RateRepository

    async def execute(
        self,
        pair: CurrencyPair,
        start: datetime,
        end: datetime,
        limit: int = 1000,
        offset: int = 0,
    ) -> Sequence[ExchangeRate]:
        if start > end:
            raise InvalidDateRange(f"start_date {start} must be <= end_date {end}")
        if (end - start) > timedelta(days=MAX_HISTORY_DAYS):
            raise InvalidDateRange(f"Date range must be <= {MAX_HISTORY_DAYS} days")
        return await self.repository.get_history(pair, start, end, limit=limit, offset=offset)
