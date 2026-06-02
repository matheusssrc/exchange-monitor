from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock

import pytest

from trillia_monitor.domain.value_objects import CurrencyPair
from trillia_monitor.infrastructure.providers.awesomeapi_client import AwesomeApiClient
from trillia_monitor.infrastructure.providers.awesomeapi_provider import (
    PROVIDER_NAME,
    AwesomeApiProvider,
)
from trillia_monitor.infrastructure.providers.exceptions import ProviderResponseInvalid


def _payload() -> dict[str, Any]:
    return {
        "USDBRL": {
            "code": "USD",
            "codein": "BRL",
            "bid": "5.1200",
            "ask": "5.1210",
            "timestamp": "1700000000",
        }
    }


@pytest.mark.asyncio
async def test_maps_payload_to_exchange_rate() -> None:
    client = AsyncMock(spec=AwesomeApiClient)
    client.fetch_last.return_value = _payload()
    provider = AwesomeApiProvider(client=client)

    rate = await provider.fetch(CurrencyPair("USD", "BRL"))

    assert rate.pair == CurrencyPair("USD", "BRL")
    assert rate.bid == Decimal("5.1200")
    assert rate.ask == Decimal("5.1210")
    assert rate.provider_name == PROVIDER_NAME
    assert rate.provider_timestamp == datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC)
    assert rate.fetched_at.tzinfo == UTC
    client.fetch_last.assert_called_once_with("USD-BRL")


@pytest.mark.asyncio
async def test_raises_when_quote_key_missing() -> None:
    client = AsyncMock(spec=AwesomeApiClient)
    client.fetch_last.return_value = {"EURBRL": _payload()["USDBRL"]}
    provider = AwesomeApiProvider(client=client)

    with pytest.raises(ProviderResponseInvalid, match="missing quote USDBRL"):
        await provider.fetch(CurrencyPair("USD", "BRL"))


@pytest.mark.asyncio
async def test_raises_when_payload_is_invalid() -> None:
    client = AsyncMock(spec=AwesomeApiClient)
    client.fetch_last.return_value = {"USDBRL": {"code": "USD"}}
    provider = AwesomeApiProvider(client=client)

    with pytest.raises(ProviderResponseInvalid):
        await provider.fetch(CurrencyPair("USD", "BRL"))
