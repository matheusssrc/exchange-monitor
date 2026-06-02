import asyncio
import signal
from collections.abc import Sequence
from contextlib import suppress

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from trillia_monitor.application.use_cases.collect_rate import CollectRateUseCase
from trillia_monitor.config import Settings, get_settings
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.observability.logging import configure_logging
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


async def run_worker(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    configure_logging(settings)
    log.info(
        "worker.starting",
        pairs=[str(p) for p in settings.monitored_pairs],
        interval_seconds=settings.polling_interval_seconds,
    )

    engine = build_engine(settings.database_url)
    session_factory = build_session_factory(engine)
    http_client = AwesomeApiClient(
        base_url=settings.awesomeapi_base_url,
        timeout_seconds=settings.provider_timeout_seconds,
        max_attempts=settings.provider_retry_attempts,
    )
    provider = AwesomeApiProvider(client=http_client)

    scheduler = AsyncIOScheduler(timezone="UTC")
    for pair in settings.monitored_pairs:
        scheduler.add_job(
            _tick,
            trigger=IntervalTrigger(seconds=settings.polling_interval_seconds),
            kwargs={
                "pair": pair,
                "provider": provider,
                "session_factory": session_factory,
                "monitored_pairs": settings.monitored_pairs,
            },
            id=f"poll-{pair}",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=settings.polling_interval_seconds,
        )

    scheduler.start()
    log.info("worker.started", jobs=[j.id for j in scheduler.get_jobs()])

    await _wait_for_shutdown()

    log.info("worker.stopping")
    scheduler.shutdown(wait=True)
    await http_client.aclose()
    await engine.dispose()
    log.info("worker.stopped")


async def _tick(
    pair: CurrencyPair,
    provider: AwesomeApiProvider,
    session_factory: async_sessionmaker[AsyncSession],
    monitored_pairs: Sequence[CurrencyPair],
) -> None:
    started = asyncio.get_running_loop().time()
    try:
        async with session_factory() as session:
            repository = SqlAlchemyRateRepository(session=session, monitored_pairs=monitored_pairs)
            use_case = CollectRateUseCase(provider=provider, repository=repository)
            await use_case.execute(pair)
        polling_success_total.labels(pair=str(pair)).inc()
    except ProviderError as exc:
        polling_failure_total.labels(pair=str(pair), reason=type(exc).__name__).inc()
        log.warning("polling.tick.failed", pair=str(pair), error=str(exc))
    except Exception:
        polling_failure_total.labels(pair=str(pair), reason="unknown").inc()
        log.exception("polling.tick.crashed", pair=str(pair))
    finally:
        elapsed = asyncio.get_running_loop().time() - started
        polling_duration_seconds.labels(pair=str(pair)).observe(elapsed)


async def _wait_for_shutdown() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _signal_handler() -> None:
        stop.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, _signal_handler)

    await stop.wait()
