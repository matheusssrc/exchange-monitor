def to_libpq_dsn(database_url: str) -> str:
    """Convert a SQLAlchemy async URL to a libpq DSN DuckDB's postgres
    extension understands (drops the '+asyncpg' driver suffix)."""
    scheme, _, rest = database_url.partition("://")
    base = scheme.split("+", 1)[0]
    return f"{base}://{rest}"
