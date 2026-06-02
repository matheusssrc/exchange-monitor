import asyncio
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.unit.application.use_cases.fakes import InMemoryRateRepository
from trillia_monitor.application.use_cases.get_latest_rate import GetLatestRateUseCase
from trillia_monitor.application.use_cases.get_rate_history import GetRateHistoryUseCase
from trillia_monitor.application.use_cases.list_pairs import ListPairsUseCase
from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.api.dependencies import (
    get_latest_rate_use_case,
    get_list_pairs_use_case,
    get_rate_history_use_case,
)
from trillia_monitor.infrastructure.api.errors import register_exception_handlers
from trillia_monitor.infrastructure.api.routers import health, pairs, rates


def _rate(day: int = 1) -> ExchangeRate:
    ts = datetime(2026, 5, day, tzinfo=UTC)
    return ExchangeRate(
        pair=CurrencyPair("USD", "BRL"),
        bid=Decimal("5.1200"),
        ask=Decimal("5.1210"),
        fetched_at=ts,
        provider_timestamp=ts,
        provider_name="awesomeapi",
    )


@pytest.fixture
def repo() -> InMemoryRateRepository:
    return InMemoryRateRepository(monitored=[CurrencyPair("USD", "BRL")])


@pytest.fixture
def app(repo: InMemoryRateRepository) -> FastAPI:
    app = FastAPI()
    app.include_router(health.router)
    app.include_router(rates.router, prefix="/rates")
    app.include_router(pairs.router, prefix="/pairs")
    register_exception_handlers(app)

    app.dependency_overrides[get_latest_rate_use_case] = lambda: GetLatestRateUseCase(repo)
    app.dependency_overrides[get_rate_history_use_case] = lambda: GetRateHistoryUseCase(repo)
    app.dependency_overrides[get_list_pairs_use_case] = lambda: ListPairsUseCase(repo)
    return app


def test_health_returns_ok(app: FastAPI) -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_latest_returns_404_when_empty(app: FastAPI) -> None:
    response = TestClient(app).get("/rates/latest")
    assert response.status_code == 404


def test_latest_returns_rate(app: FastAPI, repo: InMemoryRateRepository) -> None:
    asyncio.run(repo.save(_rate()))
    response = TestClient(app).get("/rates/latest?pair=USD-BRL")
    assert response.status_code == 200
    assert response.json()["pair"] == "USD-BRL"


def test_history_rejects_invalid_pair_format(app: FastAPI) -> None:
    response = TestClient(app).get(
        "/rates/history",
        params={
            "pair": "USDBRL",
            "start_date": "2026-05-01T00:00:00Z",
            "end_date": "2026-05-02T00:00:00Z",
        },
    )
    assert response.status_code == 422


def test_history_returns_400_when_start_after_end(app: FastAPI) -> None:
    response = TestClient(app).get(
        "/rates/history",
        params={
            "start_date": "2026-05-10T00:00:00Z",
            "end_date": "2026-05-01T00:00:00Z",
        },
    )
    assert response.status_code == 400


def test_pairs_endpoint_lists_monitored(app: FastAPI) -> None:
    response = TestClient(app).get("/pairs")
    assert response.status_code == 200
    assert response.json() == [{"pair": "USD-BRL", "base": "USD", "quote": "BRL"}]
