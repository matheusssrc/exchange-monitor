from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from trillia_monitor.application.use_cases.collect_rate import CollectRateUseCase
from trillia_monitor.application.use_cases.get_latest_rate import GetLatestRateUseCase
from trillia_monitor.application.use_cases.get_rate_history import GetRateHistoryUseCase
from trillia_monitor.application.use_cases.list_pairs import ListPairsUseCase
from trillia_monitor.config import Settings
from trillia_monitor.infrastructure.persistence.repositories import SqlAlchemyRateRepository
from trillia_monitor.infrastructure.providers.awesomeapi_provider import AwesomeApiProvider


def get_settings_dep(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    factory = request.app.state.session_factory
    async with factory() as session:
        yield session


def get_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> SqlAlchemyRateRepository:
    return SqlAlchemyRateRepository(session=session, monitored_pairs=settings.monitored_pairs)


def get_provider(request: Request) -> AwesomeApiProvider:
    return AwesomeApiProvider(client=request.app.state.http_client)


def get_collect_rate_use_case(
    provider: Annotated[AwesomeApiProvider, Depends(get_provider)],
    repository: Annotated[SqlAlchemyRateRepository, Depends(get_repository)],
) -> CollectRateUseCase:
    return CollectRateUseCase(provider=provider, repository=repository)


def get_latest_rate_use_case(
    repository: Annotated[SqlAlchemyRateRepository, Depends(get_repository)],
) -> GetLatestRateUseCase:
    return GetLatestRateUseCase(repository=repository)


def get_rate_history_use_case(
    repository: Annotated[SqlAlchemyRateRepository, Depends(get_repository)],
) -> GetRateHistoryUseCase:
    return GetRateHistoryUseCase(repository=repository)


def get_list_pairs_use_case(
    repository: Annotated[SqlAlchemyRateRepository, Depends(get_repository)],
) -> ListPairsUseCase:
    return ListPairsUseCase(repository=repository)
