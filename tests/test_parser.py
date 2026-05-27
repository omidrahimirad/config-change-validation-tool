from pathlib import Path

import pytest

from change_validator.parser import ConfigParserError, load_config, load_rules

ROOT = Path(__file__).resolve().parents[1]


def test_yaml_parser_loads_valid_config() -> None:
    config = load_config(ROOT / "configs/current/router_site_a.yaml")

    assert config["device_id"] == "RTR-SITE-A-01"
    assert config["interfaces"]["uplink"]["mtu"] == 1500


def test_parser_rejects_missing_files() -> None:
    with pytest.raises(FileNotFoundError):
        load_config(ROOT / "configs/current/missing.yaml")


def test_parser_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text("- item\n- item2\n", encoding="utf-8")

    with pytest.raises(ConfigParserError):
        load_config(config_path)


def test_load_rules_rejects_missing_rules_list(tmp_path: Path) -> None:
    rules_path = tmp_path / "rules.yaml"
    rules_path.write_text("domain: network\n", encoding="utf-8")

    with pytest.raises(ConfigParserError):
        load_rules(rules_path)
