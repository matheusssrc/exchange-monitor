from fastapi import FastAPI

from trillia_monitor.config import Settings
from trillia_monitor.infrastructure.api.app import create_app


def test_create_app_returns_fastapi_instance() -> None:
    app = create_app(Settings(_env_file=None))  # type: ignore[call-arg]
    assert isinstance(app, FastAPI)


def test_openapi_schema_has_custom_contact() -> None:
    app = create_app(Settings(_env_file=None))  # type: ignore[call-arg]
    schema = app.openapi()
    assert schema["info"]["contact"]["name"] == "Matheus"
    assert schema["info"]["license"]["name"] == "MIT"


def test_routes_registered() -> None:
    app = create_app(Settings(_env_file=None))  # type: ignore[call-arg]
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/health" in paths
    assert "/ready" in paths
    assert "/rates/latest" in paths
    assert "/rates/history" in paths
    assert "/pairs" in paths
