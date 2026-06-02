import json
import logging

import pytest
import structlog

from trillia_monitor.config import Settings
from trillia_monitor.infrastructure.observability.logging import configure_logging


def test_configure_logging_sets_json_renderer(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(Settings(log_json=True, log_level="INFO", _env_file=None))  # type: ignore[call-arg]
    structlog.get_logger().info("event.test", foo="bar")
    captured = capsys.readouterr().out.strip()
    parsed = json.loads(captured)
    assert parsed["event"] == "event.test"
    assert parsed["foo"] == "bar"
    assert parsed["level"] == "info"


def test_configure_logging_respects_log_level() -> None:
    configure_logging(Settings(log_level="WARNING", _env_file=None))  # type: ignore[call-arg]
    assert logging.getLogger().level == logging.WARNING
