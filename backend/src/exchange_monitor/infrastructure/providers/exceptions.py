class ProviderError(Exception):
    """Base for any failure talking to an external rate provider."""


class ProviderUnavailable(ProviderError):
    """Network failure, timeout, or 5xx after exhausted retries."""


class ProviderResponseInvalid(ProviderError):
    """Response parsed but did not match expected shape."""


class ProviderRateLimited(ProviderError):
    """HTTP 429 from the provider."""
