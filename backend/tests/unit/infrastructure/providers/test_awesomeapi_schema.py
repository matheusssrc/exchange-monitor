from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from trillia_monitor.infrastructure.providers.awesomeapi_schema import AwesomeApiResponse


def _payload(timestamp: str = "1700000000") -> dict[str, Any]:
    return {
        "USDBRL": {
            "code": "USD",
            "codein": "BRL",
            "bid": "5.1200",
            "ask": "5.1210",
            "timestamp": timestamp,
        }
    }


def test_parses_well_formed_payload() -> None:
    parsed = AwesomeApiResponse.parse_raw_dict(_payload())
    quote = parsed.quotes["USDBRL"]
    assert quote.code == "USD"
    assert quote.codein == "BRL"
    assert quote.bid == Decimal("5.1200")
    assert quote.ask == Decimal("5.1210")
    assert quote.timestamp == datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC)


def test_parses_multiple_pairs() -> None:
    payload = _payload()
    payload["EURBRL"] = {
        "code": "EUR",
        "codein": "BRL",
        "bid": "5.500",
        "ask": "5.510",
        "timestamp": "1700000000",
    }
    parsed = AwesomeApiResponse.parse_raw_dict(payload)
    assert set(parsed.quotes.keys()) == {"USDBRL", "EURBRL"}


def test_rejects_missing_required_fields() -> None:
    bad: dict[str, Any] = {"USDBRL": {"code": "USD", "codein": "BRL"}}
    with pytest.raises(ValidationError):
        AwesomeApiResponse.parse_raw_dict(bad)


def test_decimal_precision_preserved_from_string() -> None:
    parsed = AwesomeApiResponse.parse_raw_dict(_payload())
    quote = parsed.quotes["USDBRL"]
    assert quote.bid == Decimal("5.1200")
    assert str(quote.bid) == "5.1200"
