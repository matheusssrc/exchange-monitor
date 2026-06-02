from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from trillia_monitor.config import Settings, get_settings
from trillia_monitor.infrastructure.observability.logging import configure_logging
from trillia_monitor.infrastructure.observability.metrics import metrics_app
from trillia_monitor.infrastructure.persistence.session import (
    build_engine,
    build_session_factory,
)
from trillia_monitor.infrastructure.providers.awesomeapi_client import AwesomeApiClient

from .errors import register_exception_handlers
from .middleware import CorrelationIdMiddleware, RequestLoggingMiddleware
from .openapi import build_openapi
from .routers import health, pairs, rates


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(settings)

    engine = build_engine(settings.database_url)
    app.state.session_factory = build_session_factory(engine)
    app.state.http_client = AwesomeApiClient(
        base_url=settings.awesomeapi_base_url,
        timeout_seconds=settings.provider_timeout_seconds,
        max_attempts=settings.provider_retry_attempts,
    )
    try:
        yield
    finally:
        await app.state.http_client.aclose()
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title="Trillia Exchange Monitor",
        version="1.0.0",
        description="Continuous exchange rate monitor (BRL/USD and more).",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.settings = settings

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(rates.router, prefix="/rates", tags=["rates"])
    app.include_router(pairs.router, prefix="/pairs", tags=["pairs"])
    app.mount("/metrics", metrics_app)

    register_exception_handlers(app)
    app.openapi = lambda: build_openapi(app)  # type: ignore[method-assign]
    return app
