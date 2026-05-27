from change_validator.diff_engine import Change
from change_validator.report_generator import generate_report


def test_markdown_report_generation() -> None:
    report = generate_report(
        current={"device_id": "RTR-1", "environment": "production"},
        planned={"device_id": "RTR-1", "environment": "production"},
        changes=[Change("interfaces.uplink.mtu", 1500, 1600)],
        passed_rules=[
            {
                "rule_id": "NET-002",
                "severity": "high",
                "description": "MTU must stay between 1280 and 9000.",
            }
        ],
        failed_rules=[],
        risk_score=0,
        risk_level="Low Risk",
        decision="Approved",
        checklist={
            "Backup confirmed": "Yes",
            "Maintenance window defined": "Yes",
            "Rollback plan available": "Yes",
            "Peer review completed": "Yes",
            "Senior approval required": "No",
        },
        rollback_recommendation="No blocking validation findings detected.",
    )

    assert "# Configuration Change Validation Report" in report
    assert "## Detected Changes" in report
    assert "| Field" in report
    assert "Final decision: Approved" in report
