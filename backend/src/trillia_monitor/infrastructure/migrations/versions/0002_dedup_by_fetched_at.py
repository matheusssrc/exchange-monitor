"""switch dedup key from provider_timestamp to fetched_at

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-01

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("uq_rate_pair_provider_ts", "exchange_rates", type_="unique")
    op.create_unique_constraint(
        "uq_rate_pair_fetched_at",
        "exchange_rates",
        ["pair", "fetched_at", "provider_name"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_rate_pair_fetched_at", "exchange_rates", type_="unique")
    op.create_unique_constraint(
        "uq_rate_pair_provider_ts",
        "exchange_rates",
        ["pair", "provider_timestamp", "provider_name"],
    )
