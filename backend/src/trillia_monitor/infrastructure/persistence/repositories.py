from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from trillia_monitor.application.ports.rate_repository import RateRepository
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair

from .mappers import to_domain, to_orm
from .models import ExchangeRateModel


class SqlAlchemyRateRepository(RateRepository):
    def __init__(self, session: AsyncSession, monitored_pairs: Sequence[CurrencyPair]):
        self._session = session
        self._monitored_pairs = tuple(monitored_pairs)

    async def save(self, rate: ExchangeRate) -> None:
        orm = to_orm(rate)
        stmt = (
            pg_insert(ExchangeRateModel)
            .values(
                pair=orm.pair,
                bid=orm.bid,
                ask=orm.ask,
                fetched_at=orm.fetched_at,
                provider_timestamp=orm.provider_timestamp,
                provider_name=orm.provider_name,
            )
            .on_conflict_do_nothing(constraint="uq_rate_pair_fetched_at")
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def get_latest(self, pair: CurrencyPair) -> ExchangeRate | None:
        stmt = (
            select(ExchangeRateModel)
            .where(ExchangeRateModel.pair == str(pair))
            .order_by(desc(ExchangeRateModel.fetched_at))
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return to_domain(row) if row else None

    async def get_history(
        self,
        pair: CurrencyPair,
        start: datetime,
        end: datetime,
        limit: int = 1000,
        offset: int = 0,
    ) -> Sequence[ExchangeRate]:
        stmt = (
            select(ExchangeRateModel)
            .where(
                ExchangeRateModel.pair == str(pair),
                ExchangeRateModel.fetched_at >= start,
                ExchangeRateModel.fetched_at <= end,
            )
            .order_by(ExchangeRateModel.fetched_at)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [to_domain(row) for row in result.scalars().all()]

    async def list_monitored_pairs(self) -> Sequence[CurrencyPair]:
        return self._monitored_pairs
