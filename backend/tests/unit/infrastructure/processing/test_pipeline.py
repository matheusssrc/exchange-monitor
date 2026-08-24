from pathlib import Path

import duckdb
import pytest

from exchange_monitor.infrastructure.processing import pipeline


def _sample_csv() -> Path:
    for parent in Path(__file__).resolve().parents:
        cand = parent / "data" / "sample" / "bronze_sample.csv"
        if cand.exists():
            return cand
    raise RuntimeError("sample bronze CSV not found")


def _bronze_con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    sample = _sample_csv()
    con.execute(f"CREATE TABLE bronze AS SELECT * FROM read_csv_auto('{sample.as_posix()}')")
    return con


def test_build_silver_derives_mid_and_spread_and_filters(tmp_path: Path) -> None:
    con = _bronze_con()
    out = tmp_path / "silver"
    pipeline.build_silver(con, out_dir=out)
    rows = con.execute("SELECT pair, mid, spread FROM silver ORDER BY pair, fetched_at").fetchall()
    assert rows[0][0] == "BRL-EUR"
    assert float(rows[0][1]) == 5.56
    assert round(float(rows[0][2]), 2) == 0.02
    assert (out / "silver.parquet").exists()


def test_build_gold_computes_indicators(tmp_path: Path) -> None:
    con = _bronze_con()
    pipeline.build_silver(con, out_dir=tmp_path / "silver")
    pipeline.build_gold(con, out_dir=tmp_path / "gold")
    daily = con.execute(
        "SELECT pair, open, close, tick_count, variation_pct FROM gold_daily WHERE pair='BRL-USD'"
    ).fetchone()
    assert daily is not None
    assert daily[3] == 3
    assert float(daily[1]) == 5.11
    assert (tmp_path / "gold" / "gold_daily.parquet").exists()
    assert (tmp_path / "gold" / "gold_hourly.parquet").exists()


def test_validate_gold_flags_invalid_ratio(tmp_path: Path) -> None:
    con = _bronze_con()
    pipeline.build_silver(con, out_dir=tmp_path / "silver")
    pipeline.build_gold(con, out_dir=tmp_path / "gold")
    report = pipeline.validate_gold(con)
    assert report["daily_rows"] >= 2
    assert report["null_variation"] == 0


def test_validate_gold_raises_when_empty(tmp_path: Path) -> None:
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE bronze (pair VARCHAR, bid DOUBLE, ask DOUBLE, "
        "fetched_at TIMESTAMP, provider_timestamp TIMESTAMP, provider_name VARCHAR)"
    )
    pipeline.build_silver(con, out_dir=tmp_path / "silver")
    pipeline.build_gold(con, out_dir=tmp_path / "gold")
    with pytest.raises(ValueError):
        pipeline.validate_gold(con)
