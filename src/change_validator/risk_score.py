"""Risk scoring and approval decision mapping."""

from __future__ import annotations

SEVERITY_POINTS = {
    "critical": 40,
    "high": 25,
    "medium": 10,
    "low": 5,
}


def severity_points(severity: str) -> int:
    """Return the configured point value for a severity."""
    return SEVERITY_POINTS.get(severity.lower(), 0)


def calculate_risk_score(failed_rules: list[dict[str, object]]) -> int:
    """Calculate risk score from failed validation rules."""
    return sum(severity_points(str(rule.get("severity", ""))) for rule in failed_rules)


def risk_level(score: int) -> str:
    """Map a numeric score to an operational risk level."""
    if score <= 20:
        return "Low Risk"
    if score <= 50:
        return "Medium Risk"
    if score <= 90:
        return "High Risk"
    return "Critical Risk"


def approval_decision(score: int) -> str:
    """Map a risk score to an approval decision."""
    level = risk_level(score)
    if level == "Low Risk":
        return "Approved"
    if level == "Medium Risk":
        return "Approved with review"
    if level == "High Risk":
        return "Requires senior approval"
    return "Rejected / blocked"
