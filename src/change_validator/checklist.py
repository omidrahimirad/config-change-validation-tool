"""Approval checklist and rollback recommendation generation."""

from __future__ import annotations

from typing import Any

from change_validator.diff_engine import get_value


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def build_approval_checklist(
    planned: dict[str, Any],
    risk_level: str,
    failed_rules: list[dict[str, Any]],
) -> dict[str, str]:
    """Build a practical change-approval checklist."""
    has_critical_or_high = any(
        str(rule.get("severity", "")).lower() in {"critical", "high"}
        for rule in failed_rules
    )
    return {
        "Backup confirmed": _yes_no(bool(get_value(planned, "backup_required", False))),
        "Maintenance window defined": _yes_no(bool(get_value(planned, "maintenance_window", None))),
        "Rollback plan available": _yes_no(bool(get_value(planned, "rollback_plan", None))),
        "Peer review completed": _yes_no(not failed_rules),
        "Senior approval required": _yes_no(risk_level in {"High Risk", "Critical Risk"} or has_critical_or_high),
    }


def rollback_recommendation(
    planned: dict[str, Any],
    failed_rules: list[dict[str, Any]],
    risk_level: str,
) -> str:
    """Generate a readable rollback recommendation based on validation findings."""
    failed_severities = {str(rule.get("severity", "")).lower() for rule in failed_rules}
    rollback_plan = get_value(planned, "rollback_plan")

    if "critical" in failed_severities:
        return (
            "Block implementation until critical findings are resolved. Confirm backup status, "
            "document restoration steps, and rehearse the rollback trigger before scheduling the change."
        )

    if "high" in failed_severities or risk_level == "High Risk":
        base = (
            "Proceed only with senior approval and an engineer assigned to monitor recovery access, "
            "service alarms, and KPI drift during the maintenance window."
        )
        if rollback_plan:
            return f"{base} Use the planned rollback path: {rollback_plan}"
        return f"{base} Add a clear rollback plan before implementation."

    if failed_rules:
        return (
            "Resolve the remaining validation findings or capture an explicit peer-review waiver "
            "before implementation."
        )

    return (
        "No blocking validation findings detected. Keep the current configuration snapshot available "
        "and verify service health after implementation."
    )
