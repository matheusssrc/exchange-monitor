from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.persistence.repositories import SqlAlchemyRateRepository


def _rate(day: int = 1, hour: int = 12) -> ExchangeRate:
    ts = datetime(2026, 5, day, hour, tzinfo=UTC)
    return ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5.1200"),
        ask=Decimal("5.1210"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )


@pytest.mark.asyncio
async def test_save_and_get_latest(session: AsyncSession) -> None:
    monitored = [CurrencyPair("USD", "BRL")]
    repo = SqlAlchemyRateRepository(session=session, monitored_pairs=monitored)
    rate = _rate(day=1)

    await repo.save(rate)
    latest = await repo.get_latest(CurrencyPair("USD", "BRL"))

    assert latest == rate


@pytest.mark.asyncio
async def test_get_latest_returns_none_when_empty(session: AsyncSession) -> None:
    repo = SqlAlchemyRateRepository(
        session=session,
        monitored_pairs=[CurrencyPair("USD", "BRL")],
    )
    assert await repo.get_latest(CurrencyPair("USD", "BRL")) is None


@pytest.mark.asyncio
async def test_save_is_idempotent_on_unique_constraint(session: AsyncSession) -> None:
    repo = SqlAlchemyRateRepository(
        session=session,
        monitored_pairs=[CurrencyPair("USD", "BRL")],
    )
    rate = _rate(day=1)
    await repo.save(rate)
    await repo.save(rate)
    await repo.save(rate)
    history = await repo.get_history(
        CurrencyPair("USD", "BRL"),
        datetime(2026, 5, 1, tzinfo=UTC),
        datetime(2026, 5, 1, 23, 59, tzinfo=UTC),
    )
    assert len(history) == 1


@pytest.mark.asyncio
async def test_get_history_filters_and_orders_by_fetched_at(session: AsyncSession) -> None:
    repo = SqlAlchemyRateRepository(
        session=session,
        monitored_pairs=[CurrencyPair("USD", "BRL")],
    )
    for d in (1, 5, 10, 15):
        await repo.save(_rate(day=d))
    history = await repo.get_history(
        CurrencyPair("USD", "BRL"),
        datetime(2026, 5, 5, tzinfo=UTC),
        datetime(2026, 5, 10, 23, 59, tzinfo=UTC),
    )
    assert [r.fetched_at.day for r in history] == [5, 10]


@pytest.mark.asyncio
async def test_get_history_pagination(session: AsyncSession) -> None:
    repo = SqlAlchemyRateRepository(
        session=session,
        monitored_pairs=[CurrencyPair("USD", "BRL")],
    )
    for h in range(24):
        await repo.save(_rate(day=1, hour=h))
    page1 = await repo.get_history(
        CurrencyPair("USD", "BRL"),
        datetime(2026, 5, 1, tzinfo=UTC),
        datetime(2026, 5, 1, 23, 59, tzinfo=UTC),
        limit=10,
        offset=0,
    )
    page2 = await repo.get_history(
        CurrencyPair("USD", "BRL"),
        datetime(2026, 5, 1, tzinfo=UTC),
        datetime(2026, 5, 1, 23, 59, tzinfo=UTC),
        limit=10,
        offset=10,
    )
    assert len(page1) == 10
    assert len(page2) == 10
    assert {r.fetched_at.hour for r in page1}.isdisjoint({r.fetched_at.hour for r in page2})


@pytest.mark.asyncio
async def test_list_monitored_pairs_returns_configured_list(session: AsyncSession) -> None:
    monitored = [CurrencyPair("USD", "BRL"), CurrencyPair("EUR", "BRL")]
    repo = SqlAlchemyRateRepository(session=session, monitored_pairs=monitored)
    assert list(await repo.list_monitored_pairs()) == monitored
