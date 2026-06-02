from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from trillia_monitor.infrastructure.persistence.session import (
    build_engine,
    build_session_factory,
)


def test_build_engine_returns_async_engine() -> None:
    engine = build_engine("sqlite+aiosqlite:///:memory:")
    assert isinstance(engine, AsyncEngine)


def test_build_session_factory_returns_sessionmaker() -> None:
    engine = build_engine("sqlite+aiosqlite:///:memory:")
    factory = build_session_factory(engine)
    assert isinstance(factory, async_sessionmaker)
    session = factory()
    assert isinstance(session, AsyncSession)
