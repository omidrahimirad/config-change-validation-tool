from change_validator.diff_engine import Change
from change_validator.report_generator import generate_report, write_report


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


def test_report_generation_includes_failed_rule_and_write_report(tmp_path) -> None:
    output_path = tmp_path / "reports" / "change.md"
    report = generate_report(
        current={"system_id": "CTRL-1", "environment": "production"},
        planned={"system_id": "CTRL-1", "environment": "production"},
        changes=[],
        passed_rules=[],
        failed_rules=[
            {
                "rule_id": "OPS-001",
                "severity": "critical",
                "description": "Production changes require a maintenance window.",
                "finding": "maintenance_window is required for production changes.",
            }
        ],
        risk_score=40,
        risk_level="Medium Risk",
        decision="Approved with review",
        checklist={
            "Backup confirmed": "No",
            "Maintenance window defined": "No",
            "Rollback plan available": "No",
            "Peer review completed": "No",
            "Senior approval required": "Yes",
        },
        rollback_recommendation="Block implementation until critical findings are resolved.",
    )

    written_path = write_report(report, output_path)

    assert written_path == output_path
    assert output_path.read_text(encoding="utf-8") == report
    assert "_None._" in report
    assert "OPS-001" in report
