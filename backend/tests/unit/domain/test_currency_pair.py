from dataclasses import FrozenInstanceError

import pytest

from trillia_monitor.domain.value_objects import CurrencyPair


class TestCurrencyPairConstruction:
    def test_creates_with_valid_codes(self) -> None:
        pair = CurrencyPair(base="USD", quote="BRL")
        assert pair.base == "USD"
        assert pair.quote == "BRL"

    @pytest.mark.parametrize(
        "base,quote",
        [("US", "BRL"), ("USDX", "BRL"), ("USD", "BR"), ("USD", "BRLX")],
    )
    def test_rejects_codes_with_wrong_length(self, base: str, quote: str) -> None:
        with pytest.raises(ValueError, match="3 chars"):
            CurrencyPair(base=base, quote=quote)

    def test_rejects_identical_base_and_quote(self) -> None:
        with pytest.raises(ValueError, match="differ"):
            CurrencyPair(base="USD", quote="USD")

    def test_is_frozen(self) -> None:
        pair = CurrencyPair(base="USD", quote="BRL")
        with pytest.raises(FrozenInstanceError):
            pair.base = "EUR"  # type: ignore[misc]


class TestCurrencyPairParse:
    def test_parses_uppercase_hyphenated_form(self) -> None:
        assert CurrencyPair.parse("USD-BRL") == CurrencyPair(base="USD", quote="BRL")

    def test_normalizes_lowercase(self) -> None:
        assert CurrencyPair.parse("usd-brl") == CurrencyPair(base="USD", quote="BRL")

    @pytest.mark.parametrize("bad", ["USDBRL", "USD/BRL", "USD-BRL-EUR", ""])
    def test_rejects_invalid_format(self, bad: str) -> None:
        with pytest.raises(ValueError):
            CurrencyPair.parse(bad)


class TestCurrencyPairStr:
    def test_str_returns_hyphenated_form(self) -> None:
        assert str(CurrencyPair(base="USD", quote="BRL")) == "USD-BRL"
