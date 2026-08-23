import argparse
import asyncio
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="exchange-monitor")
    parser.add_argument(
        "command",
        choices=(
            "api",
            "worker",
            "migrate",
            "collect",
            "build-silver",
            "build-gold",
            "validate-gold",
        ),
    )
    parser.add_argument("pair", nargs="?", default=None)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    if args.command == "api":
        return _run_api(args.host, args.port)
    if args.command == "worker":
        return asyncio.run(_run_worker())
    if args.command == "migrate":
        from exchange_monitor.config import get_settings

        return _run_migrations(get_settings().database_url)
    if args.command == "collect":
        if not args.pair:
            parser.error("collect requires a pair, e.g. 'collect BRL-USD'")
        return _run_collect(args.pair)
    if args.command in ("build-silver", "build-gold", "validate-gold"):
        step_by_command = {
            "build-silver": "silver",
            "build-gold": "gold",
            "validate-gold": "validate",
        }
        _run_medallion(step_by_command[args.command])
        return 0
    return 1


def _run_api(host: str, port: int) -> int:
    import uvicorn

    from exchange_monitor.infrastructure.api.app import create_app

    uvicorn.run(create_app(), host=host, port=port, log_config=None, access_log=False)
    return 0


async def _run_worker() -> int:
    from exchange_monitor.infrastructure.scheduler.worker import run_worker

    await run_worker()
    return 0


def _run_collect(pair: str) -> int:
    from exchange_monitor.infrastructure.scheduler.collect import collect_pair

    collect_pair(pair)
    return 0


def _run_migrations(database_url: str) -> int:
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    cfg_path = Path(__file__).parent / "infrastructure" / "migrations" / "alembic.ini"
    if not cfg_path.exists():
        cfg_path = Path(__file__).parent.parent.parent / "alembic.ini"
    cfg = Config(str(cfg_path))
    cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(cfg, "head")
    return 0


def _run_medallion(step: str) -> None:
    import duckdb
    import structlog

    from exchange_monitor.config import get_settings
    from exchange_monitor.infrastructure.processing import pipeline

    settings = get_settings()
    silver_dir = f"{settings.data_dir}/silver"
    gold_dir = f"{settings.data_dir}/gold"
    con = duckdb.connect()
    if step in ("silver", "validate"):
        pipeline.attach_bronze_from_postgres(con, settings.database_url)
        pipeline.build_silver(con, out_dir=silver_dir)
    if step in ("gold", "validate"):
        con.execute(
            "CREATE OR REPLACE TABLE silver AS "
            f"SELECT * FROM read_parquet('{silver_dir}/silver.parquet')"
        )
        pipeline.build_gold(con, out_dir=gold_dir)
    if step == "validate":
        report = pipeline.validate_gold(con)
        structlog.get_logger().info("medallion.validate", **report)


if __name__ == "__main__":
    sys.exit(main())
