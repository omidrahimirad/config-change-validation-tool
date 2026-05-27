from change_validator.risk_score import approval_decision, calculate_risk_score, risk_level


def test_risk_score_calculation() -> None:
    failed_rules = [
        {"severity": "critical"},
        {"severity": "high"},
        {"severity": "medium"},
        {"severity": "low"},
    ]

    assert calculate_risk_score(failed_rules) == 80


def test_approval_decision_mapping() -> None:
    assert risk_level(0) == "Low Risk"
    assert approval_decision(20) == "Approved"
    assert approval_decision(21) == "Approved with review"
    assert approval_decision(51) == "Requires senior approval"
    assert approval_decision(91) == "Rejected / blocked"
