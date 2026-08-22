from pathlib import Path
from typing import Any

import duckdb

from exchange_monitor.infrastructure.processing import pipeline


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "queries" / "q1_variacao_diaria.sql").exists():
            return parent
    raise RuntimeError("repo root not found")


def _gold_dir(tmp_path: Path) -> Path:
    root = _repo_root()
    con = duckdb.connect()
    sample = root / "data" / "sample" / "bronze_sample.csv"
    con.execute(f"CREATE TABLE bronze AS SELECT * FROM read_csv_auto('{sample.as_posix()}')")
    pipeline.build_silver(con, out_dir=tmp_path / "silver")
    pipeline.build_gold(con, out_dir=tmp_path / "gold")
    return tmp_path / "gold"


def _run_query(name: str, gold_dir: Path) -> list[tuple[Any, ...]]:
    daily = (gold_dir / "gold_daily.parquet").as_posix()
    raw = (_repo_root() / "queries" / name).read_text(encoding="utf-8")
    sql = raw.replace("DAILY_PARQUET", daily)
    return duckdb.connect().execute(sql).fetchall()


def test_q1_returns_one_row_per_pair_day(tmp_path: Path) -> None:
    rows = _run_query("q1_variacao_diaria.sql", _gold_dir(tmp_path))
    assert len(rows) == 2


def test_q2_ranks_pairs_by_volatility(tmp_path: Path) -> None:
    rows = _run_query("q2_ranking_volatilidade.sql", _gold_dir(tmp_path))
    assert {r[0] for r in rows} == {"BRL-USD", "BRL-EUR"}


def test_q3_reports_spread_and_range(tmp_path: Path) -> None:
    rows = _run_query("q3_spread_min_max.sql", _gold_dir(tmp_path))
    assert all(r[5] >= 0 for r in rows)
