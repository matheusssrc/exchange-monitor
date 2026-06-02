import asyncio

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine

from trillia_monitor.application.use_cases.collect_rate import CollectRateUseCase
from trillia_monitor.config import Settings, get_settings
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.observability.metrics import (
    polling_duration_seconds,
    polling_failure_total,
    polling_success_total,
)
from trillia_monitor.infrastructure.persistence.repositories import SqlAlchemyRateRepository
from trillia_monitor.infrastructure.persistence.session import (
    build_engine,
    build_session_factory,
)
from trillia_monitor.infrastructure.providers.awesomeapi_client import AwesomeApiClient
from trillia_monitor.infrastructure.providers.awesomeapi_provider import AwesomeApiProvider
from trillia_monitor.infrastructure.providers.exceptions import ProviderError

log = structlog.get_logger()


def _build_provider(settings: Settings) -> tuple[AwesomeApiProvider, AwesomeApiClient]:
    client = AwesomeApiClient(
        base_url=settings.awesomeapi_base_url,
        timeout_seconds=settings.provider_timeout_seconds,
        max_attempts=settings.provider_retry_attempts,
    )
    return AwesomeApiProvider(client=client), client


async def _dispose_engine(engine: AsyncEngine) -> None:
    await engine.dispose()


def collect_pair(pair_code: str, settings: Settings | None = None) -> None:
    """Synchronous one-shot collection for a single pair.

    Designed to be called from an Airflow task: it builds its own engine and
    HTTP client, runs the shared CollectRateUseCase once, records metrics, and
    disposes resources. Provider/transport failures are logged and counted but
    never re-raised, so one bad pair cannot fail the whole DAG run.
    """
    resolved = settings or get_settings()
    asyncio.run(_collect_pair_async(CurrencyPair.parse(pair_code), resolved))


async def _collect_pair_async(pair: CurrencyPair, settings: Settings) -> None:
    started = asyncio.get_running_loop().time()
    engine = build_engine(settings.database_url)
    session_factory = build_session_factory(engine)
    provider, client = _build_provider(settings)
    try:
        async with session_factory() as session:
            repository = SqlAlchemyRateRepository(
                session=session, monitored_pairs=settings.monitored_pairs
            )
            use_case = CollectRateUseCase(provider=provider, repository=repository)
            await use_case.execute(pair)
        polling_success_total.labels(pair=str(pair)).inc()
    except ProviderError as exc:
        polling_failure_total.labels(pair=str(pair), reason=type(exc).__name__).inc()
        log.warning("collect.failed", pair=str(pair), error=str(exc))
    except Exception:
        polling_failure_total.labels(pair=str(pair), reason="unknown").inc()
        log.exception("collect.crashed", pair=str(pair))
    finally:
        elapsed = asyncio.get_running_loop().time() - started
        polling_duration_seconds.labels(pair=str(pair)).observe(elapsed)
        await client.aclose()
        await _dispose_engine(engine)
