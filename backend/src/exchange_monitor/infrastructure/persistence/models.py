from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ExchangeRateModel(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pair: Mapped[str] = mapped_column(String(7), nullable=False)
    bid: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=8), nullable=False)
    ask: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=8), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provider_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "pair",
            "fetched_at",
            "provider_name",
            name="uq_rate_pair_fetched_at",
        ),
        Index("ix_rate_pair_fetched_at", "pair", "fetched_at"),
        Index("ix_rate_pair_provider_ts_desc", "pair", "provider_timestamp"),
    )
