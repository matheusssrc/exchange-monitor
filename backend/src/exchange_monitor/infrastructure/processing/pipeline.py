from pathlib import Path
from typing import Any

import duckdb

from .duckdb_dsn import to_libpq_dsn


def _sql_dir() -> Path:
    """SQL files ship inside the package (next to this module), so they are
    available whether running from source, an installed wheel, or a container."""
    return Path(__file__).resolve().parent / "sql"


def _run_sql_file(con: duckdb.DuckDBPyConnection, name: str) -> None:
    con.execute((_sql_dir() / name).read_text(encoding="utf-8"))


def _scalar(con: duckdb.DuckDBPyConnection, sql: str) -> Any:
    row = con.execute(sql).fetchone()
    if row is None:
        raise RuntimeError(f"query returned no rows: {sql}")
    return row[0]


def attach_bronze_from_postgres(con: duckdb.DuckDBPyConnection, database_url: str) -> None:
    """Expose the Postgres exchange_rates table as a DuckDB view `bronze`."""
    dsn = to_libpq_dsn(database_url)
    con.execute("INSTALL postgres; LOAD postgres;")
    con.execute(f"ATTACH '{dsn}' AS pg (TYPE postgres, READ_ONLY)")
    con.execute("CREATE OR REPLACE VIEW bronze AS SELECT * FROM pg.exchange_rates")


def build_silver(con: duckdb.DuckDBPyConnection, *, out_dir: str | Path) -> None:
    _run_sql_file(con, "build_silver.sql")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    con.execute(
        f"COPY silver TO '{(out / 'silver.parquet').as_posix()}' (FORMAT PARQUET)"
    )


def build_gold(con: duckdb.DuckDBPyConnection, *, out_dir: str | Path) -> None:
    _run_sql_file(con, "build_gold.sql")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    con.execute(
        f"COPY gold_daily TO '{(out / 'gold_daily.parquet').as_posix()}' (FORMAT PARQUET)"
    )
    con.execute(
        f"COPY gold_hourly TO '{(out / 'gold_hourly.parquet').as_posix()}' (FORMAT PARQUET)"
    )


def validate_gold(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    daily_rows = _scalar(con, "SELECT count(*) FROM gold_daily")
    null_variation = _scalar(
        con, "SELECT count(*) FROM gold_daily WHERE variation_pct IS NULL"
    )
    report = {"daily_rows": daily_rows, "null_variation": null_variation}
    if daily_rows == 0:
        raise ValueError("gold validation failed: gold_daily is empty")
    return report
