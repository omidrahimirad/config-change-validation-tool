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
