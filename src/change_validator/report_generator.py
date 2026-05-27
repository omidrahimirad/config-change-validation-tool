"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from change_validator.diff_engine import Change, get_value


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return f"`{value}`"
    return str(value)


def _change_risk(field: str, failed_rules: list[dict[str, Any]]) -> str:
    field_lower = field.lower()
    for rule in failed_rules:
        finding = str(rule.get("finding", "")).lower()
        description = str(rule.get("description", "")).lower()
        if field_lower in finding or any(part in description for part in field_lower.split(".")):
            return str(rule.get("severity", "low")).title()
    return "Low"


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_None._"
    frame = pd.DataFrame(rows, columns=columns)
    return frame.to_markdown(index=False)


def generate_report(
    current: dict[str, Any],
    planned: dict[str, Any],
    changes: list[Change],
    passed_rules: list[dict[str, Any]],
    failed_rules: list[dict[str, Any]],
    risk_score: int,
    risk_level: str,
    decision: str,
    checklist: dict[str, str],
    rollback_recommendation: str,
) -> str:
    """Generate a complete Markdown change validation report."""
    identifier = (
        get_value(planned, "device_id")
        or get_value(planned, "cell_id")
        or get_value(planned, "system_id")
        or "Unknown"
    )
    environment = get_value(planned, "environment", get_value(planned, "site", "Unknown"))
    status = "Passed" if not failed_rules else "Failed"

    change_rows = [
        {
            "Field": change.field,
            "Current Value": _format_value(change.current_value),
            "Planned Value": _format_value(change.planned_value),
            "Risk": _change_risk(change.field, failed_rules),
        }
        for change in changes
    ]
    passed_rows = [
        {
            "Rule ID": rule["rule_id"],
            "Severity": str(rule["severity"]).title(),
            "Description": rule["description"],
        }
        for rule in passed_rules
    ]
    failed_rows = [
        {
            "Rule ID": rule["rule_id"],
            "Severity": str(rule["severity"]).title(),
            "Description": rule["description"],
            "Finding": rule["finding"],
        }
        for rule in failed_rules
    ]

    checklist_lines = "\n".join(f"- {key}: {value}" for key, value in checklist.items())

    return f"""# Configuration Change Validation Report

## Change Summary
- Device/System: {identifier}
- Environment: {environment}
- Changed fields: {len(changes)}
- Validation status: {status}
- Risk level: {risk_level}
- Final decision: {decision}

## Detected Changes
{_markdown_table(change_rows, ["Field", "Current Value", "Planned Value", "Risk"])}

## Passed Validation Rules
{_markdown_table(passed_rows, ["Rule ID", "Severity", "Description"])}

## Failed Validation Rules
{_markdown_table(failed_rows, ["Rule ID", "Severity", "Description", "Finding"])}

## Risk Score
- Total score: {risk_score}
- Risk level: {risk_level}

## Approval Checklist
{checklist_lines}

## Rollback Recommendation
{rollback_recommendation}
"""


def write_report(markdown: str, output_path: str | Path) -> Path:
    """Write report content to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path
