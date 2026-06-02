import argparse
import asyncio
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trillia-monitor")
    parser.add_argument("command", choices=("api", "worker", "migrate", "collect"))
    parser.add_argument("pair", nargs="?", default=None)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    if args.command == "api":
        return _run_api(args.host, args.port)
    if args.command == "worker":
        return asyncio.run(_run_worker())
    if args.command == "migrate":
        from trillia_monitor.config import get_settings

        return _run_migrations(get_settings().database_url)
    if args.command == "collect":
        if not args.pair:
            parser.error("collect requires a pair, e.g. 'collect BRL-USD'")
        return _run_collect(args.pair)
    return 1


def _run_api(host: str, port: int) -> int:
    import uvicorn

    from trillia_monitor.infrastructure.api.app import create_app

    uvicorn.run(create_app(), host=host, port=port, log_config=None, access_log=False)
    return 0


async def _run_worker() -> int:
    from trillia_monitor.infrastructure.scheduler.worker import run_worker

    await run_worker()
    return 0


def _run_collect(pair: str) -> int:
    from trillia_monitor.infrastructure.scheduler.collect import collect_pair

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


if __name__ == "__main__":
    sys.exit(main())
