import pytest

from trillia_monitor.application.ports.rate_provider import RateProvider
from trillia_monitor.application.ports.rate_repository import RateRepository


def test_rate_repository_is_abstract() -> None:
    with pytest.raises(TypeError):
        RateRepository()  # type: ignore[abstract]


def test_rate_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        RateProvider()  # type: ignore[abstract]


def test_rate_repository_declares_required_methods() -> None:
    methods = RateRepository.__abstractmethods__
    assert {"save", "get_latest", "get_history", "list_monitored_pairs"} <= methods


def test_rate_provider_declares_required_methods() -> None:
    methods = RateProvider.__abstractmethods__
    assert {"fetch"} <= methods
