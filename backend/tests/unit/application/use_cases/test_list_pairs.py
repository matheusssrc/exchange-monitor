import pytest

from trillia_monitor.application.use_cases.list_pairs import ListPairsUseCase
from trillia_monitor.domain.value_objects import CurrencyPair

from .fakes import InMemoryRateRepository


@pytest.mark.asyncio
async def test_returns_monitored_pairs_from_repository() -> None:
    pairs = [CurrencyPair("USD", "BRL"), CurrencyPair("EUR", "BRL")]
    repo = InMemoryRateRepository(monitored=pairs)
    use_case = ListPairsUseCase(repository=repo)
    assert list(await use_case.execute()) == pairs


@pytest.mark.asyncio
async def test_returns_empty_list_when_no_pairs_configured() -> None:
    repo = InMemoryRateRepository(monitored=[])
    use_case = ListPairsUseCase(repository=repo)
    assert list(await use_case.execute()) == []
