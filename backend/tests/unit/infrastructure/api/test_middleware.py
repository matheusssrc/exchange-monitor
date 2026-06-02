from fastapi import FastAPI
from fastapi.testclient import TestClient

from trillia_monitor.infrastructure.api.middleware import (
    CORRELATION_HEADER,
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
)


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"pong": "ok"}

    return app


def test_correlation_header_generated_when_missing() -> None:
    client = TestClient(_build_app())
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.headers[CORRELATION_HEADER]


def test_correlation_header_propagated_when_provided() -> None:
    client = TestClient(_build_app())
    response = client.get("/ping", headers={CORRELATION_HEADER: "abc-123"})
    assert response.headers[CORRELATION_HEADER] == "abc-123"
