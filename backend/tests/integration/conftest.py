import os
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from exchange_monitor.infrastructure.persistence.models import Base


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    # In CI a Postgres service is provided via EXCHANGE_DATABASE_URL; use it
    # directly. Locally, fall back to spinning an ephemeral container.
    env_url = os.environ.get("EXCHANGE_DATABASE_URL")
    if env_url:
        yield env_url
        return
    with PostgresContainer("postgres:16-alpine") as container:
        yield container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest_asyncio.fixture
async def engine(postgres_url: str) -> AsyncIterator[AsyncEngine]:
    eng = create_async_engine(postgres_url)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        yield s
