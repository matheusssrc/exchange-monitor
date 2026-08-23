import json
from datetime import datetime
from pathlib import Path
from typing import Any


class JsonlBronzeSink:
    """Lands the raw provider payload as append-only JSONL, partitioned
    by pair and UTC date. This is the untransformed Bronze evidence."""

    def __init__(self, base_dir: str | Path):
        self._base_dir = Path(base_dir)

    def write(self, pair: str, payload: dict[str, Any], fetched_at: datetime) -> None:
        day = fetched_at.date().isoformat()
        out_dir = self._base_dir / pair
        out_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "pair": pair,
            "fetched_at": fetched_at.isoformat(),
            "payload": payload,
        }
        with (out_dir / f"{day}.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
