import json
from datetime import UTC, datetime
from pathlib import Path

from exchange_monitor.infrastructure.bronze.raw_sink import JsonlBronzeSink


def test_writes_payload_as_jsonl_partitioned_by_pair_and_date(tmp_path: Path) -> None:
    sink = JsonlBronzeSink(base_dir=tmp_path)
    payload = {"BRLUSD": {"code": "BRL", "codein": "USD", "bid": "5.1", "ask": "5.12"}}
    fetched_at = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)

    sink.write("BRL-USD", payload, fetched_at)

    out = tmp_path / "BRL-USD" / "2026-08-20.jsonl"
    assert out.exists()
    line = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert line["pair"] == "BRL-USD"
    assert line["fetched_at"] == "2026-08-20T12:00:00+00:00"
    assert line["payload"] == payload


def test_appends_without_overwriting(tmp_path: Path) -> None:
    sink = JsonlBronzeSink(base_dir=tmp_path)
    ts = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
    sink.write("BRL-USD", {"a": 1}, ts)
    sink.write("BRL-USD", {"a": 2}, ts)
    out = tmp_path / "BRL-USD" / "2026-08-20.jsonl"
    assert len(out.read_text(encoding="utf-8").splitlines()) == 2
