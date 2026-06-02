from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from trillia_monitor.application.use_cases.get_latest_rate import GetLatestRateUseCase
from trillia_monitor.application.use_cases.get_rate_history import GetRateHistoryUseCase
from trillia_monitor.domain.value_objects import CurrencyPair

from ..dependencies import get_latest_rate_use_case, get_rate_history_use_case
from ..schemas import ErrorOut, HistoryPage, RateOut

router = APIRouter()


@router.get(
    "/latest",
    response_model=RateOut,
    summary="Get the most recent rate",
    responses={404: {"model": ErrorOut}},
)
async def latest(
    use_case: Annotated[GetLatestRateUseCase, Depends(get_latest_rate_use_case)],
    pair: Annotated[str, Query(pattern=r"^[A-Za-z]{3}-[A-Za-z]{3}$")] = "USD-BRL",
) -> RateOut:
    parsed = CurrencyPair.parse(pair)
    rate = await use_case.execute(parsed)
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "rate_not_found", "message": f"No rate stored for {pair}"},
        )
    return RateOut.from_domain(rate)


@router.get(
    "/history",
    response_model=HistoryPage,
    summary="Get historical rates within a date range",
    responses={400: {"model": ErrorOut}},
)
async def history(
    use_case: Annotated[GetRateHistoryUseCase, Depends(get_rate_history_use_case)],
    start_date: Annotated[datetime, Query(description="Inclusive lower bound (UTC)")],
    end_date: Annotated[datetime, Query(description="Inclusive upper bound (UTC)")],
    pair: Annotated[str, Query(pattern=r"^[A-Za-z]{3}-[A-Za-z]{3}$")] = "USD-BRL",
    limit: Annotated[int, Query(ge=1, le=10_000)] = 1000,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> HistoryPage:
    parsed = CurrencyPair.parse(pair)
    rates = await use_case.execute(parsed, start_date, end_date, limit=limit, offset=offset)
    return HistoryPage(
        pair=str(parsed),
        start=start_date,
        end=end_date,
        count=len(rates),
        items=[RateOut.from_domain(r) for r in rates],
    )
