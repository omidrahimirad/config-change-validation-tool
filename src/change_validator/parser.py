"""Configuration and rule file parsing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigParserError(ValueError):
    """Raised when a configuration or rules file cannot be parsed."""


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return a dictionary."""
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"File not found: {yaml_path}")

    with yaml_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ConfigParserError(f"Expected a YAML mapping in {yaml_path}")

    return data


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a current or planned configuration file."""
    return load_yaml_file(path)


def load_rules(path: str | Path) -> list[dict[str, Any]]:
    """Load validation rules from a YAML file."""
    data = load_yaml_file(path)
    rules = data.get("rules")
    if not isinstance(rules, list):
        raise ConfigParserError("Rules file must contain a top-level 'rules' list")
    return rules
