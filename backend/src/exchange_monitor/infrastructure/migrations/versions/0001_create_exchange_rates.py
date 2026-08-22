"""create exchange_rates table

Revision ID: 0001
Revises:
Create Date: 2026-05-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("pair", sa.String(length=7), nullable=False),
        sa.Column("bid", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("ask", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provider_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provider_name", sa.String(length=32), nullable=False),
        sa.UniqueConstraint(
            "pair",
            "provider_timestamp",
            "provider_name",
            name="uq_rate_pair_provider_ts",
        ),
    )
    op.create_index(
        "ix_rate_pair_fetched_at",
        "exchange_rates",
        ["pair", "fetched_at"],
    )
    op.create_index(
        "ix_rate_pair_provider_ts_desc",
        "exchange_rates",
        ["pair", "provider_timestamp"],
    )


def downgrade() -> None:
    op.drop_index("ix_rate_pair_provider_ts_desc", table_name="exchange_rates")
    op.drop_index("ix_rate_pair_fetched_at", table_name="exchange_rates")
    op.drop_table("exchange_rates")
