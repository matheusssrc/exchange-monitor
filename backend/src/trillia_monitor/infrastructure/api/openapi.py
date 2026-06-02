from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def build_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=(
            "REST API for the Trillia Exchange Monitor.\n\n"
            "Polls one or more currency pairs from AwesomeAPI on a configurable interval, "
            "persists the history in PostgreSQL, and exposes the latest and historical rates."
        ),
        routes=app.routes,
    )
    schema["info"]["contact"] = {
        "name": "Matheus",
        "url": "https://github.com/matheusssrc/trillia-exchange-monitor",
    }
    schema["info"]["license"] = {"name": "MIT"}
    schema["tags"] = [
        {"name": "rates", "description": "Current and historical exchange rates."},
        {"name": "pairs", "description": "Currency pairs currently monitored."},
        {"name": "meta", "description": "Health, readiness, and Prometheus metrics."},
    ]
    app.openapi_schema = schema
    return schema
