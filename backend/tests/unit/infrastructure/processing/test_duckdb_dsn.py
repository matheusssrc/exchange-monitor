from exchange_monitor.infrastructure.processing.duckdb_dsn import to_libpq_dsn


def test_strips_async_driver() -> None:
    url = "postgresql+asyncpg://exchange:exchange@db:5432/exchange"
    assert to_libpq_dsn(url) == "postgresql://exchange:exchange@db:5432/exchange"


def test_leaves_plain_url_untouched() -> None:
    url = "postgresql://u:p@h:5432/d"
    assert to_libpq_dsn(url) == url
