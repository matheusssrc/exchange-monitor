from unittest.mock import patch

import pytest

from trillia_monitor.__main__ import main


def test_main_rejects_invalid_command() -> None:
    with pytest.raises(SystemExit):
        main(["unknown"])


def test_main_routes_api_command() -> None:
    with patch("trillia_monitor.__main__._run_api") as run_api:
        run_api.return_value = 0
        assert main(["api"]) == 0
        run_api.assert_called_once()


def test_main_routes_worker_command() -> None:
    with (
        patch("trillia_monitor.__main__.asyncio.run") as run_loop,
        patch("trillia_monitor.__main__._run_worker") as run_worker_factory,
    ):
        run_loop.return_value = 0
        assert main(["worker"]) == 0
        run_loop.assert_called_once()
        run_worker_factory.assert_called_once()


def test_main_routes_migrate_command() -> None:
    with patch("trillia_monitor.__main__._run_migrations") as run_mig:
        run_mig.return_value = 0
        assert main(["migrate"]) == 0
        run_mig.assert_called_once()


def test_main_routes_collect_command() -> None:
    with patch("trillia_monitor.__main__._run_collect") as run_collect:
        run_collect.return_value = 0
        assert main(["collect", "BRL-USD"]) == 0
        run_collect.assert_called_once_with("BRL-USD")


def test_main_collect_requires_pair() -> None:
    with pytest.raises(SystemExit):
        main(["collect"])
