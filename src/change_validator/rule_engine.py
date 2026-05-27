"""YAML-driven validation rule engine."""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address, ip_interface
from typing import Any

from change_validator.diff_engine import Change, get_value


@dataclass(frozen=True)
class RuleResult:
    """Result of evaluating one validation rule."""

    rule_id: str
    severity: str
    description: str
    passed: bool
    finding: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "description": self.description,
            "passed": self.passed,
            "finding": self.finding,
        }


def _changed_fields(changes: list[Change]) -> set[str]:
    return {change.field for change in changes}


def _changed_prefixes(changes: list[Change]) -> set[str]:
    fields = _changed_fields(changes)
    prefixes: set[str] = set(fields)
    for field in fields:
        parts = field.split(".")
        for index in range(1, len(parts)):
            prefixes.add(".".join(parts[:index]))
    return prefixes


def _is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def evaluate_rules(
    current: dict[str, Any],
    planned: dict[str, Any],
    rules: list[dict[str, Any]],
    changes: list[Change],
) -> list[RuleResult]:
    """Evaluate all YAML rules against current and planned configuration."""
    results: list[RuleResult] = []
    changed_fields = _changed_fields(changes)
    changed_prefixes = _changed_prefixes(changes)

    for rule in rules:
        check_type = str(rule.get("check_type", ""))
        field = str(rule.get("field", ""))
        severity = str(rule.get("severity", "low")).lower()
        rule_id = str(rule.get("id", "UNKNOWN"))
        description = str(rule.get("description", "No description supplied"))

        planned_value = get_value(planned, field)
        current_value = get_value(current, field)
        passed, finding = _evaluate_rule(
            check_type=check_type,
            field=field,
            current_value=current_value,
            planned_value=planned_value,
            rule=rule,
            changed_fields=changed_fields,
            changed_prefixes=changed_prefixes,
            planned=planned,
        )
        results.append(
            RuleResult(
                rule_id=rule_id,
                severity=severity,
                description=description,
                passed=passed,
                finding=finding,
            )
        )

    return results


def _evaluate_rule(
    check_type: str,
    field: str,
    current_value: Any,
    planned_value: Any,
    rule: dict[str, Any],
    changed_fields: set[str],
    changed_prefixes: set[str],
    planned: dict[str, Any],
) -> tuple[bool, str]:
    if check_type == "range":
        return _check_range(field, planned_value, rule)
    if check_type == "must_equal":
        expected = rule.get("expected")
        passed = planned_value == expected
        return passed, "" if passed else f"{field} is {planned_value!r}; expected {expected!r}."
    if check_type == "not_empty":
        passed = not _is_empty(planned_value)
        return passed, "" if passed else f"{field} must not be empty."
    if check_type == "max_delta":
        return _check_max_delta(field, current_value, planned_value, rule)
    if check_type == "no_change_without_approval":
        return _check_no_change_without_approval(field, current_value, planned_value, rule, planned)
    if check_type == "subnet_consistency":
        return _check_subnet_consistency(rule, planned)
    if check_type == "required_if_environment_production":
        return _check_required_for_production(field, planned_value, planned)
    if check_type == "requires_rollback_plan":
        return _check_requires_rollback_plan(
            field, current_value, planned_value, changed_prefixes, planned
        )
    if check_type == "required_if_risk_high":
        return _check_required_if_risk_high(
            field, planned_value, changed_fields, changed_prefixes, rule
        )

    return False, f"Unsupported check type: {check_type}"


def _check_range(field: str, value: Any, rule: dict[str, Any]) -> tuple[bool, str]:
    minimum = rule.get("min")
    maximum = rule.get("max")
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return False, f"{field} value {value!r} is not numeric."

    if minimum is not None and numeric_value < float(minimum):
        return False, f"{field} is {value}; minimum allowed is {minimum}."
    if maximum is not None and numeric_value > float(maximum):
        return False, f"{field} is {value}; maximum allowed is {maximum}."
    return True, ""


def _check_max_delta(
    field: str, current_value: Any, planned_value: Any, rule: dict[str, Any]
) -> tuple[bool, str]:
    max_delta = float(rule.get("max_delta", 0))
    try:
        delta = abs(float(planned_value) - float(current_value))
    except (TypeError, ValueError):
        return False, f"{field} current/planned values must be numeric."

    passed = delta <= max_delta
    return (
        passed,
        "" if passed else f"{field} changes by {delta:g}; allowed delta is {max_delta:g}.",
    )


def _check_no_change_without_approval(
    field: str,
    current_value: Any,
    planned_value: Any,
    rule: dict[str, Any],
    planned: dict[str, Any],
) -> tuple[bool, str]:
    if current_value == planned_value:
        return True, ""

    approval_field = str(rule.get("approval_field", "approval.management_ip_change_approved"))
    approved = bool(get_value(planned, approval_field, False))
    if approved:
        return True, ""
    return False, f"{field} changed from {current_value!r} to {planned_value!r} without approval."


def _check_subnet_consistency(rule: dict[str, Any], planned: dict[str, Any]) -> tuple[bool, str]:
    interface_field = str(rule.get("interface_field", "interfaces.uplink.ip_address"))
    gateway_field = str(rule.get("gateway_field", "default_gateway"))
    interface_value = get_value(planned, interface_field)
    gateway_value = get_value(planned, gateway_field)

    try:
        network = ip_interface(str(interface_value)).network
        gateway = ip_address(str(gateway_value))
    except ValueError as exc:
        return False, f"Could not evaluate subnet consistency: {exc}"

    if gateway in network:
        return True, ""
    return False, f"Default gateway {gateway} is not reachable within {network}."


def _check_required_for_production(
    field: str, value: Any, planned: dict[str, Any]
) -> tuple[bool, str]:
    environment = str(get_value(planned, "environment", "")).lower()
    if environment != "production":
        return True, ""
    passed = not _is_empty(value)
    return passed, "" if passed else f"{field} is required for production changes."


def _check_requires_rollback_plan(
    field: str,
    current_value: Any,
    planned_value: Any,
    changed_prefixes: set[str],
    planned: dict[str, Any],
) -> tuple[bool, str]:
    if field not in changed_prefixes and current_value == planned_value:
        return True, ""
    rollback_plan = get_value(planned, "rollback_plan")
    if rollback_plan:
        return True, ""
    return False, f"{field} changed and no rollback_plan is defined."


def _check_required_if_risk_high(
    field: str,
    value: Any,
    changed_fields: set[str],
    changed_prefixes: set[str],
    rule: dict[str, Any],
) -> tuple[bool, str]:
    trigger_fields = [str(item) for item in rule.get("trigger_fields", [])]
    triggered = bool(set(trigger_fields) & (changed_fields | changed_prefixes))
    if not triggered:
        return True, ""
    passed = not _is_empty(value)
    return passed, "" if passed else f"{field} is required because high-risk fields changed."


def split_results(results: list[RuleResult]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return passed and failed rules as report-friendly dictionaries."""
    passed = [result.as_dict() for result in results if result.passed]
    failed = [result.as_dict() for result in results if not result.passed]
    return passed, failed
