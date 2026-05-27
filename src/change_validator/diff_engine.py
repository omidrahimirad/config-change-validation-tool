"""Recursive configuration diffing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Change:
    """A changed field between current and planned configuration."""

    field: str
    current_value: Any
    planned_value: Any


def get_value(data: dict[str, Any], field_path: str, default: Any = None) -> Any:
    """Read a dotted path from a nested dictionary."""
    value: Any = data
    for part in field_path.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return default
    return value


def flatten_config(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested dictionaries into dotted field paths."""
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flattened.update(flatten_config(value, path))
        else:
            flattened[path] = value
    return flattened


def diff_configs(current: dict[str, Any], planned: dict[str, Any]) -> list[Change]:
    """Return all field-level changes between two configurations."""
    current_flat = flatten_config(current)
    planned_flat = flatten_config(planned)
    all_fields = sorted(set(current_flat) | set(planned_flat))

    changes: list[Change] = []
    for field in all_fields:
        current_value = current_flat.get(field)
        planned_value = planned_flat.get(field)
        if current_value != planned_value:
            changes.append(Change(field, current_value, planned_value))
    return changes
