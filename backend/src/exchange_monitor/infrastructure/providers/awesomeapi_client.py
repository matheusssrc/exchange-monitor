from typing import Any

import httpx
import structlog
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from .exceptions import ProviderRateLimited, ProviderUnavailable

log = structlog.get_logger()

_TRANSIENT_HTTPX = (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError)


def _log_before_sleep(state: RetryCallState) -> None:
    exc = state.outcome.exception() if state.outcome else None
    log.warning(
        "provider.retry",
        attempt=state.attempt_number,
        error=str(exc) if exc else None,
    )


class AwesomeApiClient:
    def __init__(
        self,
        base_url: str = "https://economia.awesomeapi.com.br",
        timeout_seconds: float = 5.0,
        max_attempts: int = 4,
        backoff_initial: float = 0.5,
        backoff_max: float = 8.0,
    ):
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds, connect=2.0),
            headers={"User-Agent": "trillia-exchange-monitor/1.0"},
        )
        self._retry_policy = AsyncRetrying(
            reraise=True,
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential_jitter(initial=backoff_initial, max=backoff_max),
            retry=retry_if_exception_type((ProviderUnavailable, ProviderRateLimited)),
            before_sleep=_log_before_sleep,
        )

    async def fetch_last(self, pair_path: str) -> dict[str, Any]:
        async for attempt in self._retry_policy:
            with attempt:
                return await self._do_fetch(pair_path)
        raise ProviderUnavailable(f"unreachable after retries: {pair_path}")

    async def _do_fetch(self, pair_path: str) -> dict[str, Any]:
        try:
            response = await self._client.get(f"/last/{pair_path}")
        except _TRANSIENT_HTTPX as exc:
            raise ProviderUnavailable(str(exc)) from exc

        if response.status_code == 429:
            raise ProviderRateLimited(f"rate limited on {pair_path}")
        if 500 <= response.status_code < 600:
            raise ProviderUnavailable(f"{response.status_code} on {pair_path}")
        if response.status_code >= 400:
            raise ProviderUnavailable(
                f"unexpected status {response.status_code} on {pair_path}: {response.text[:200]}"
            )

        return response.json()  # type: ignore[no-any-return]

    async def aclose(self) -> None:
        await self._client.aclose()
