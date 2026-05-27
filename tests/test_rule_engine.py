from change_validator.diff_engine import diff_configs
from change_validator.rule_engine import evaluate_rules, split_results


def _run_rule(current: dict, planned: dict, rule: dict) -> tuple[list[dict], list[dict]]:
    changes = diff_configs(current, planned)
    results = evaluate_rules(current, planned, [rule], changes)
    return split_results(results)


def test_range_rule_passes_and_fails_correctly() -> None:
    rule = {
        "id": "TEST-RANGE",
        "severity": "high",
        "description": "MTU range",
        "check_type": "range",
        "field": "mtu",
        "min": 1280,
        "max": 9000,
    }

    passed, failed = _run_rule({"mtu": 1500}, {"mtu": 1600}, rule)
    assert len(passed) == 1
    assert failed == []

    passed, failed = _run_rule({"mtu": 1500}, {"mtu": 9500}, rule)
    assert passed == []
    assert failed[0]["rule_id"] == "TEST-RANGE"


def test_must_equal_rule_passes_and_fails_correctly() -> None:
    rule = {
        "id": "TEST-EQUAL",
        "severity": "critical",
        "description": "SSH remains enabled",
        "check_type": "must_equal",
        "field": "ssh.enabled",
        "expected": True,
    }

    passed, failed = _run_rule({"ssh": {"enabled": True}}, {"ssh": {"enabled": True}}, rule)
    assert len(passed) == 1
    assert failed == []

    passed, failed = _run_rule({"ssh": {"enabled": True}}, {"ssh": {"enabled": False}}, rule)
    assert passed == []
    assert "expected" in failed[0]["finding"]


def test_not_empty_rule_passes_and_fails_correctly() -> None:
    rule = {
        "id": "TEST-NOT-EMPTY",
        "severity": "high",
        "description": "Neighbors required",
        "check_type": "not_empty",
        "field": "neighbor_cells",
    }

    passed, failed = _run_rule({"neighbor_cells": ["A"]}, {"neighbor_cells": ["A", "B"]}, rule)
    assert len(passed) == 1
    assert failed == []

    passed, failed = _run_rule({"neighbor_cells": ["A"]}, {"neighbor_cells": []}, rule)
    assert passed == []
    assert "must not be empty" in failed[0]["finding"]


def test_max_delta_rule_passes_and_fails_correctly() -> None:
    rule = {
        "id": "TEST-DELTA",
        "severity": "high",
        "description": "Power delta",
        "check_type": "max_delta",
        "field": "max_tx_power_dbm",
        "max_delta": 3,
    }

    passed, failed = _run_rule({"max_tx_power_dbm": 43}, {"max_tx_power_dbm": 45}, rule)
    assert len(passed) == 1
    assert failed == []

    passed, failed = _run_rule({"max_tx_power_dbm": 43}, {"max_tx_power_dbm": 48}, rule)
    assert passed == []
    assert "allowed delta" in failed[0]["finding"]


def test_no_change_without_approval_requires_approval_when_field_changes() -> None:
    rule = {
        "id": "TEST-APPROVAL",
        "severity": "critical",
        "description": "Management IP approval",
        "check_type": "no_change_without_approval",
        "field": "management_ip",
        "approval_field": "approval.management_ip_change_approved",
    }

    passed, failed = _run_rule(
        {"management_ip": "10.0.0.1"},
        {"management_ip": "10.0.0.2", "approval": {"management_ip_change_approved": False}},
        rule,
    )
    assert passed == []
    assert "without approval" in failed[0]["finding"]

    passed, failed = _run_rule(
        {"management_ip": "10.0.0.1"},
        {"management_ip": "10.0.0.2", "approval": {"management_ip_change_approved": True}},
        rule,
    )
    assert len(passed) == 1
    assert failed == []


def test_subnet_consistency_detects_unreachable_gateway() -> None:
    rule = {
        "id": "TEST-SUBNET",
        "severity": "high",
        "description": "Gateway in subnet",
        "check_type": "subnet_consistency",
        "field": "default_gateway",
        "interface_field": "interfaces.uplink.ip_address",
        "gateway_field": "default_gateway",
    }
    planned = {
        "interfaces": {"uplink": {"ip_address": "172.16.20.2/24"}},
        "default_gateway": "172.16.10.1",
    }

    passed, failed = _run_rule(planned, planned, rule)

    assert passed == []
    assert "not reachable" in failed[0]["finding"]


def test_required_for_production_and_required_if_risk_high() -> None:
    production_window_rule = {
        "id": "TEST-PROD",
        "severity": "critical",
        "description": "Production window",
        "check_type": "required_if_environment_production",
        "field": "maintenance_window",
    }
    rollback_rule = {
        "id": "TEST-ROLLBACK",
        "severity": "critical",
        "description": "Rollback required",
        "check_type": "required_if_risk_high",
        "field": "rollback_plan",
        "trigger_fields": ["default_gateway"],
    }

    passed, failed = _run_rule(
        {"environment": "production", "default_gateway": "10.0.0.1"},
        {"environment": "production", "default_gateway": "10.0.0.2"},
        production_window_rule,
    )
    assert passed == []
    assert "required for production" in failed[0]["finding"]

    passed, failed = _run_rule(
        {"default_gateway": "10.0.0.1"},
        {"default_gateway": "10.0.0.2", "rollback_plan": ""},
        rollback_rule,
    )
    assert passed == []
    assert "required because high-risk fields changed" in failed[0]["finding"]


def test_requires_rollback_plan_for_changed_tac_and_unsupported_rule() -> None:
    rollback_rule = {
        "id": "TEST-TAC",
        "severity": "critical",
        "description": "TAC rollback",
        "check_type": "requires_rollback_plan",
        "field": "tac",
    }
    unsupported_rule = {
        "id": "TEST-UNKNOWN",
        "severity": "low",
        "description": "Unknown check",
        "check_type": "unknown",
        "field": "tac",
    }

    passed, failed = _run_rule({"tac": 1}, {"tac": 2}, rollback_rule)
    assert passed == []
    assert "no rollback_plan" in failed[0]["finding"]

    passed, failed = _run_rule({"tac": 1}, {"tac": 1}, unsupported_rule)
    assert passed == []
    assert "Unsupported check type" in failed[0]["finding"]
