from pathlib import Path

from change_validator.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_validate_generates_report(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "router_report.md"

    exit_code = main(
        [
            "validate",
            "--current",
            str(ROOT / "configs/current/router_site_a.yaml"),
            "--planned",
            str(ROOT / "configs/planned/router_site_a.yaml"),
            "--rules",
            str(ROOT / "rules/network_rules.yaml"),
            "--output",
            str(output_path),
        ]
    )

    terminal_output = capsys.readouterr().out

    assert exit_code == 0
    assert "Validation completed." in terminal_output
    assert "Risk score: 75" in terminal_output
    assert output_path.exists()
    assert "Configuration Change Validation Report" in output_path.read_text(encoding="utf-8")
