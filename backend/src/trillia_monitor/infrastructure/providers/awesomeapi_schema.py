from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AwesomeApiQuote(BaseModel):
    code: str
    codein: str
    bid: Decimal
    ask: Decimal
    timestamp: datetime

    @field_validator("timestamp", mode="before")
    @classmethod
    def _ts_from_unix(cls, value: str | int | datetime) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromtimestamp(int(value), tz=UTC)

    @field_validator("bid", "ask", mode="before")
    @classmethod
    def _decimal_from_str(cls, value: str | Decimal) -> Decimal:
        return Decimal(value) if isinstance(value, str) else value


class AwesomeApiResponse(BaseModel):
    quotes: dict[str, AwesomeApiQuote] = Field(default_factory=dict)

    @classmethod
    def parse_raw_dict(cls, payload: dict[str, Any]) -> "AwesomeApiResponse":
        return cls(quotes={k: AwesomeApiQuote(**v) for k, v in payload.items()})
