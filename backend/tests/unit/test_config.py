import pytest
from pydantic import ValidationError

from trillia_monitor.config import Settings
from trillia_monitor.domain.value_objects import CurrencyPair


def test_defaults_have_usd_brl_pair() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.monitored_pairs == [CurrencyPair("USD", "BRL")]


def test_parses_comma_separated_pairs_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRILLIA_MONITORED_PAIRS", "USD-BRL,EUR-BRL,GBP-BRL")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.monitored_pairs == [
        CurrencyPair("USD", "BRL"),
        CurrencyPair("EUR", "BRL"),
        CurrencyPair("GBP", "BRL"),
    ]


def test_polling_interval_must_be_in_range(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRILLIA_POLLING_INTERVAL_SECONDS", "1")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_env_prefix_isolates_unrelated_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "should-be-ignored")
    monkeypatch.setenv("TRILLIA_DATABASE_URL", "postgresql+asyncpg://u:p@h:5432/d")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.database_url == "postgresql+asyncpg://u:p@h:5432/d"
