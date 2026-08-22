from prometheus_client import CollectorRegistry, Counter, Histogram, make_asgi_app

registry = CollectorRegistry()

polling_success_total = Counter(
    "trillia_polling_success_total",
    "Successful polling ticks per pair",
    labelnames=("pair",),
    registry=registry,
)

polling_failure_total = Counter(
    "trillia_polling_failure_total",
    "Failed polling ticks per pair",
    labelnames=("pair", "reason"),
    registry=registry,
)

polling_duration_seconds = Histogram(
    "trillia_polling_duration_seconds",
    "Polling tick duration in seconds",
    labelnames=("pair",),
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)

metrics_app = make_asgi_app(registry=registry)
