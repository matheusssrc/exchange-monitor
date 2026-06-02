from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from trillia_monitor.domain.entities import ExchangeRate


class RateOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "pair": "USD-BRL",
                    "bid": "5.1200",
                    "ask": "5.1210",
                    "mid": "5.1205",
                    "fetched_at": "2026-05-27T18:00:00+00:00",
                    "provider_timestamp": "2026-05-27T17:59:58+00:00",
                    "provider_name": "awesomeapi",
                }
            ]
        }
    )

    pair: str
    bid: Decimal
    ask: Decimal
    mid: Decimal
    fetched_at: datetime
    provider_timestamp: datetime
    provider_name: str

    @classmethod
    def from_domain(cls, rate: ExchangeRate) -> "RateOut":
        return cls(
            pair=str(rate.pair),
            bid=rate.bid,
            ask=rate.ask,
            mid=rate.mid,
            fetched_at=rate.fetched_at,
            provider_timestamp=rate.provider_timestamp,
            provider_name=rate.provider_name,
        )


class HistoryPage(BaseModel):
    pair: str
    start: datetime
    end: datetime
    count: int
    items: list[RateOut]


class PairOut(BaseModel):
    pair: str
    base: str
    quote: str


class ErrorOut(BaseModel):
    error: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable description")
    details: dict[str, Any] | None = None
