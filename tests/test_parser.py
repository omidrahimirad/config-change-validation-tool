from pathlib import Path

import pytest

from change_validator.parser import load_config

ROOT = Path(__file__).resolve().parents[1]


def test_yaml_parser_loads_valid_config() -> None:
    config = load_config(ROOT / "configs/current/router_site_a.yaml")

    assert config["device_id"] == "RTR-SITE-A-01"
    assert config["interfaces"]["uplink"]["mtu"] == 1500


def test_parser_rejects_missing_files() -> None:
    with pytest.raises(FileNotFoundError):
        load_config(ROOT / "configs/current/missing.yaml")
