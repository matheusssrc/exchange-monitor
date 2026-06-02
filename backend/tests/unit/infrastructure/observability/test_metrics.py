from prometheus_client import Counter, Histogram

from trillia_monitor.infrastructure.observability.metrics import (
    metrics_app,
    polling_duration_seconds,
    polling_failure_total,
    polling_success_total,
    registry,
)


def test_counters_and_histogram_defined() -> None:
    assert isinstance(polling_success_total, Counter)
    assert isinstance(polling_failure_total, Counter)
    assert isinstance(polling_duration_seconds, Histogram)


def test_metrics_app_is_asgi_callable() -> None:
    assert callable(metrics_app)


def test_counters_can_be_incremented() -> None:
    polling_success_total.labels(pair="USD-BRL").inc()
    polling_failure_total.labels(pair="USD-BRL", reason="unknown").inc()
    polling_duration_seconds.labels(pair="USD-BRL").observe(0.1)


def test_metrics_share_isolated_registry() -> None:
    names = {m.name for m in registry.collect()}
    assert {
        "trillia_polling_success",
        "trillia_polling_failure",
        "trillia_polling_duration_seconds",
    } <= names
