from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import inspect

from trillia_monitor.infrastructure.persistence.models import Base, ExchangeRateModel


def test_table_name() -> None:
    assert ExchangeRateModel.__tablename__ == "exchange_rates"


def test_required_columns_exist() -> None:
    columns = {c.name for c in inspect(ExchangeRateModel).columns}
    assert columns == {
        "id",
        "pair",
        "bid",
        "ask",
        "fetched_at",
        "provider_timestamp",
        "provider_name",
    }


def test_unique_constraint_defined() -> None:
    constraints = {c.name for c in ExchangeRateModel.__table__.constraints}
    assert "uq_rate_pair_fetched_at" in constraints


def test_indexes_defined() -> None:
    indexes = {i.name for i in ExchangeRateModel.__table__.indexes}
    assert "ix_rate_pair_fetched_at" in indexes
    assert "ix_rate_pair_provider_ts_desc" in indexes


def test_instance_can_be_constructed() -> None:
    now = datetime.now(tz=UTC)
    obj = ExchangeRateModel(
        pair="USD-BRL",
        bid=Decimal("5.12"),
        ask=Decimal("5.13"),
        fetched_at=now,
        provider_timestamp=now,
        provider_name="awesomeapi",
    )
    assert obj.pair == "USD-BRL"


def test_base_metadata_includes_table() -> None:
    assert "exchange_rates" in Base.metadata.tables
