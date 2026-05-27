"""Command-line interface for configuration change validation."""

from __future__ import annotations

import argparse
from pathlib import Path

from change_validator.checklist import build_approval_checklist, rollback_recommendation
from change_validator.diff_engine import diff_configs
from change_validator.parser import load_config, load_rules
from change_validator.report_generator import generate_report, write_report
from change_validator.risk_score import approval_decision, calculate_risk_score, risk_level
from change_validator.rule_engine import evaluate_rules, split_results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="change_validator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a planned configuration change")
    validate.add_argument("--current", required=True, help="Current configuration YAML path")
    validate.add_argument("--planned", required=True, help="Planned configuration YAML path")
    validate.add_argument("--rules", required=True, help="Validation rules YAML path")
    validate.add_argument("--output", required=True, help="Markdown report output path")
    return parser


def run_validation(args: argparse.Namespace) -> int:
    current = load_config(args.current)
    planned = load_config(args.planned)
    rules = load_rules(args.rules)

    changes = diff_configs(current, planned)
    results = evaluate_rules(current, planned, rules, changes)
    passed_rules, failed_rules = split_results(results)

    score = calculate_risk_score(failed_rules)
    level = risk_level(score)
    decision = approval_decision(score)
    checklist = build_approval_checklist(planned, level, failed_rules)
    recommendation = rollback_recommendation(planned, failed_rules, level)

    markdown = generate_report(
        current=current,
        planned=planned,
        changes=changes,
        passed_rules=passed_rules,
        failed_rules=failed_rules,
        risk_score=score,
        risk_level=level,
        decision=decision,
        checklist=checklist,
        rollback_recommendation=recommendation,
    )
    output_path = write_report(markdown, args.output)

    print("Validation completed.")
    print()
    print(f"Changed fields: {len(changes)}")
    print(f"Passed checks: {len(passed_rules)}")
    print(f"Failed checks: {len(failed_rules)}")
    print(f"Risk score: {score}")
    print(f"Risk level: {level.upper().replace(' RISK', '')}")
    print(f"Decision: {decision.upper()}")
    print()
    print("Report saved to:")
    print(Path(output_path))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return run_validation(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
