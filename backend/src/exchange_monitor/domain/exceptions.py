class DomainError(Exception):
    """Base class for all domain-level errors."""


class InvalidCurrencyPair(DomainError):
    """Currency pair value or format is not acceptable."""


class RateNotFound(DomainError):
    """No persisted rate matches the requested query."""


class InvalidDateRange(DomainError):
    """The provided date range is invalid (negative or too large)."""
