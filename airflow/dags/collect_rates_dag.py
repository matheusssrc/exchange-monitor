"""Trillia exchange-rate collection DAG.

Runs on a configurable interval (TRILLIA_POLLING_INTERVAL_SECONDS, default 30s)
and fans out one mapped Bash task per monitored pair. Each task invokes the
backend CLI inside an isolated virtualenv (/opt/trillia/venv), which keeps the
backend's SQLAlchemy 2.0 dependency away from Airflow's own SQLAlchemy 1.4
environment. The CLI reuses CollectRateUseCase via collect_pair.

Airflow is the orchestrator that replaces the former APScheduler worker
(see ADR-0009; ADR-0003 superseded).

This module imports only `airflow` and the stdlib — never `trillia_monitor` —
so parsing the DAG does not pull SQLAlchemy 2.0 into the scheduler/webserver.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator

VENV_PYTHON = "/opt/trillia/venv/bin/python"
DEFAULT_PAIRS = "BRL-USD,BRL-EUR,BRL-ARS,BRL-UYU,USD-BRL,USD-EUR,USD-ARS,USD-UYU"


def _monitored_pairs() -> list[str]:
    raw = os.environ.get("TRILLIA_MONITORED_PAIRS", DEFAULT_PAIRS)
    return [pair.strip() for pair in raw.split(",") if pair.strip()]


def _poll_interval() -> timedelta:
    try:
        seconds = int(os.environ.get("TRILLIA_POLLING_INTERVAL_SECONDS", "30"))
    except ValueError:
        seconds = 30
    return timedelta(seconds=max(seconds, 5))


@dag(
    dag_id="collect_rates",
    description="Poll AwesomeAPI for every monitored currency pair and persist it.",
    schedule=_poll_interval(),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=20)},
    tags=["trillia", "exchange-rates"],
)
def collect_rates() -> None:
    BashOperator.partial(task_id="collect").expand(
        bash_command=[
            f"{VENV_PYTHON} -m trillia_monitor collect {pair}"
            for pair in _monitored_pairs()
        ],
    )


collect_rates()
