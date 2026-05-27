from change_validator.checklist import build_approval_checklist, rollback_recommendation


def test_approval_checklist_marks_readiness_and_senior_approval() -> None:
    checklist = build_approval_checklist(
        {
            "backup_required": True,
            "maintenance_window": "2026-06-07 01:00-03:00 Europe/Berlin",
            "rollback_plan": "Restore previous snapshot.",
        },
        "High Risk",
        [{"severity": "high"}],
    )

    assert checklist["Backup confirmed"] == "Yes"
    assert checklist["Maintenance window defined"] == "Yes"
    assert checklist["Rollback plan available"] == "Yes"
    assert checklist["Peer review completed"] == "No"
    assert checklist["Senior approval required"] == "Yes"


def test_rollback_recommendations_reflect_failure_severity() -> None:
    critical = rollback_recommendation({}, [{"severity": "critical"}], "Critical Risk")
    high = rollback_recommendation(
        {"rollback_plan": "Restore previous RAN export."},
        [{"severity": "high"}],
        "High Risk",
    )
    clean = rollback_recommendation({}, [], "Low Risk")

    assert "Block implementation" in critical
    assert "Restore previous RAN export" in high
    assert "No blocking validation findings" in clean
