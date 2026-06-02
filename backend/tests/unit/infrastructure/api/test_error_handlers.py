from fastapi import FastAPI
from fastapi.testclient import TestClient

from trillia_monitor.domain.exceptions import (
    InvalidCurrencyPair,
    InvalidDateRange,
    RateNotFound,
)
from trillia_monitor.infrastructure.api.errors import register_exception_handlers
from trillia_monitor.infrastructure.providers.exceptions import (
    ProviderResponseInvalid,
    ProviderUnavailable,
)


def _build_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-invalid-pair")
    def _ipair() -> None:
        raise InvalidCurrencyPair("bad pair")

    @app.get("/raise-invalid-range")
    def _irange() -> None:
        raise InvalidDateRange("bad range")

    @app.get("/raise-not-found")
    def _nf() -> None:
        raise RateNotFound("none")

    @app.get("/raise-provider-down")
    def _pd() -> None:
        raise ProviderUnavailable("upstream down")

    @app.get("/raise-provider-invalid")
    def _pi() -> None:
        raise ProviderResponseInvalid("garbage")

    return app


def test_invalid_pair_maps_to_400() -> None:
    response = TestClient(_build_app()).get("/raise-invalid-pair")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_currency_pair"


def test_invalid_range_maps_to_400() -> None:
    response = TestClient(_build_app()).get("/raise-invalid-range")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_date_range"


def test_rate_not_found_maps_to_404() -> None:
    response = TestClient(_build_app()).get("/raise-not-found")
    assert response.status_code == 404
    assert response.json()["error"] == "rate_not_found"


def test_provider_unavailable_maps_to_502() -> None:
    response = TestClient(_build_app()).get("/raise-provider-down")
    assert response.status_code == 502
    assert response.json()["error"] == "provider_unavailable"


def test_provider_response_invalid_maps_to_502() -> None:
    response = TestClient(_build_app()).get("/raise-provider-invalid")
    assert response.status_code == 502
    assert response.json()["error"] == "provider_response_invalid"
