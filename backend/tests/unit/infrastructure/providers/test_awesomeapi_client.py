from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
import respx

from trillia_monitor.infrastructure.providers.awesomeapi_client import AwesomeApiClient
from trillia_monitor.infrastructure.providers.exceptions import (
    ProviderRateLimited,
    ProviderUnavailable,
)


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AwesomeApiClient]:
    instance = AwesomeApiClient(
        base_url="https://provider.test",
        timeout_seconds=2.0,
        max_attempts=3,
        backoff_initial=0.01,
        backoff_max=0.05,
    )
    yield instance
    await instance.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_returns_json_on_success(client: AwesomeApiClient) -> None:
    respx.get("https://provider.test/last/USD-BRL").mock(
        return_value=httpx.Response(200, json={"USDBRL": {"bid": "5.0"}})
    )
    payload = await client.fetch_last("USD-BRL")
    assert payload == {"USDBRL": {"bid": "5.0"}}


@pytest.mark.asyncio
@respx.mock
async def test_retries_then_succeeds(client: AwesomeApiClient) -> None:
    route = respx.get("https://provider.test/last/USD-BRL").mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(500),
            httpx.Response(200, json={"USDBRL": {"ok": True}}),
        ]
    )
    payload = await client.fetch_last("USD-BRL")
    assert payload == {"USDBRL": {"ok": True}}
    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_raises_unavailable_after_max_attempts(client: AwesomeApiClient) -> None:
    respx.get("https://provider.test/last/USD-BRL").mock(return_value=httpx.Response(500))
    with pytest.raises(ProviderUnavailable):
        await client.fetch_last("USD-BRL")


@pytest.mark.asyncio
@respx.mock
async def test_raises_rate_limited_on_429(client: AwesomeApiClient) -> None:
    respx.get("https://provider.test/last/USD-BRL").mock(return_value=httpx.Response(429))
    with pytest.raises((ProviderRateLimited, ProviderUnavailable)):
        await client.fetch_last("USD-BRL")


@pytest.mark.asyncio
@respx.mock
async def test_treats_timeout_as_unavailable(client: AwesomeApiClient) -> None:
    respx.get("https://provider.test/last/USD-BRL").mock(
        side_effect=httpx.TimeoutException("timeout")
    )
    with pytest.raises(ProviderUnavailable):
        await client.fetch_last("USD-BRL")
