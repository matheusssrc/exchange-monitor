"""Medallion build DAG: Bronze (exchange_rates) -> Silver -> Gold -> validate.

Dependent tasks guarantee a stage never runs before the previous one finished.
Each task shells out to the backend CLI inside the isolated venv, matching the
collect_rates DAG pattern (keeps SQLAlchemy 2.0 out of the Airflow env)."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator

VENV_PYTHON = "/opt/exchange/venv/bin/python"


@dag(
    dag_id="build_medallion",
    description="Build Silver and Gold medallion layers from Bronze and validate.",
    schedule=timedelta(minutes=5),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=30)},
    tags=["exchange", "medallion"],
)
def build_medallion() -> None:
    silver = BashOperator(
        task_id="build_silver",
        bash_command=f"{VENV_PYTHON} -m exchange_monitor build-silver",
    )
    gold = BashOperator(
        task_id="build_gold",
        bash_command=f"{VENV_PYTHON} -m exchange_monitor build-gold",
    )
    validate = BashOperator(
        task_id="validate_gold",
        bash_command=f"{VENV_PYTHON} -m exchange_monitor validate-gold",
    )
    silver >> gold >> validate


build_medallion()
