from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .value_objects import CurrencyPair


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    pair: CurrencyPair
    bid: Decimal
    ask: Decimal
    fetched_at: datetime
    provider_timestamp: datetime
    provider_name: str

    def __post_init__(self) -> None:
        if self.bid <= 0 or self.ask <= 0:
            raise ValueError("Rates must be positive")
        if self.ask < self.bid:
            raise ValueError("Ask must be >= bid")
        if self.fetched_at.tzinfo is None or self.provider_timestamp.tzinfo is None:
            raise ValueError("Timestamps must be timezone-aware (UTC)")

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / 2
