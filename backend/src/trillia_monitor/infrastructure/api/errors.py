from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from trillia_monitor.domain.exceptions import (
    InvalidCurrencyPair,
    InvalidDateRange,
    RateNotFound,
)
from trillia_monitor.infrastructure.providers.exceptions import (
    ProviderError,
    ProviderResponseInvalid,
    ProviderUnavailable,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidCurrencyPair)
    async def _invalid_pair(_: Request, exc: InvalidCurrencyPair) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "invalid_currency_pair", "message": str(exc)},
        )

    @app.exception_handler(InvalidDateRange)
    async def _invalid_range(_: Request, exc: InvalidDateRange) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "invalid_date_range", "message": str(exc)},
        )

    @app.exception_handler(RateNotFound)
    async def _not_found(_: Request, exc: RateNotFound) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "rate_not_found", "message": str(exc)},
        )

    @app.exception_handler(ProviderUnavailable)
    async def _provider_down(_: Request, exc: ProviderUnavailable) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "provider_unavailable", "message": str(exc)},
        )

    @app.exception_handler(ProviderResponseInvalid)
    async def _provider_invalid(_: Request, exc: ProviderResponseInvalid) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "provider_response_invalid", "message": str(exc)},
        )

    @app.exception_handler(ProviderError)
    async def _provider_generic(_: Request, exc: ProviderError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "provider_error", "message": str(exc)},
        )
