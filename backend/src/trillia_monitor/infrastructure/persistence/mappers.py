from trillia_monitor.domain.entities import ExchangeRate
from trillia_monitor.domain.value_objects import CurrencyPair

from .models import ExchangeRateModel


def to_domain(row: ExchangeRateModel) -> ExchangeRate:
    return ExchangeRate(
        pair=CurrencyPair.parse(row.pair),
        bid=row.bid,
        ask=row.ask,
        fetched_at=row.fetched_at,
        provider_timestamp=row.provider_timestamp,
        provider_name=row.provider_name,
    )


def to_orm(rate: ExchangeRate) -> ExchangeRateModel:
    return ExchangeRateModel(
        pair=str(rate.pair),
        bid=rate.bid,
        ask=rate.ask,
        fetched_at=rate.fetched_at,
        provider_timestamp=rate.provider_timestamp,
        provider_name=rate.provider_name,
    )
