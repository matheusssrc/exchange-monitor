from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CurrencyPair:
    base: str
    quote: str

    def __post_init__(self) -> None:
        if not (len(self.base) == 3 and len(self.quote) == 3):
            raise ValueError("Currency codes must be 3 chars (ISO 4217-ish)")
        if self.base == self.quote:
            raise ValueError("Base and quote must differ")

    @classmethod
    def parse(cls, value: str) -> "CurrencyPair":
        try:
            base, quote = value.upper().split("-")
        except ValueError as exc:
            raise ValueError(f"Invalid pair format '{value}', expected 'BASE-QUOTE'") from exc
        return cls(base=base, quote=quote)

    def __str__(self) -> str:
        return f"{self.base}-{self.quote}"
