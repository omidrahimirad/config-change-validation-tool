# Design Trade-offs

This project is intentionally scoped as an offline configuration validation CLI. The goal is to demonstrate reproducible engineering review logic without pretending to be a production change-management platform.

## Why YAML Rules

YAML rules keep validation logic transparent and reviewable. A reviewer can inspect the policy checks without reading Python code, and teams can adapt limits, severities, and field paths for different example domains. This also makes the rule layer suitable for code review because policy changes are represented as small text diffs.

## Why No Database

The tool is focused on reproducible file-based workflows: input configurations, validation rules, and generated reports. A database would add operational state, migrations, and deployment concerns that are outside the purpose of this repository. For a pre-check CLI, files are easier to version, test, review, and reproduce.

## Why No Live Device Integration

The project avoids connecting to real devices because its purpose is safe offline pre-check validation. It compares proposed files before implementation and produces evidence for review. Live integration would require credentials, lab access, vendor behavior handling, retry logic, and security controls that should not be mixed into a portfolio-safe example.

## Why Markdown Reports

Markdown reports are portable, readable in GitHub, easy to diff, and useful for change-control documentation. They can be attached to tickets, reviewed in pull requests, and archived without requiring a report server or proprietary viewer.

## Why Rule-Based Validation Instead of ML

Configuration validation needs deterministic and explainable logic. A blocked change should be traceable to a specific rule, field, severity, and finding. Probabilistic predictions would make approval decisions harder to audit and would not be appropriate for this kind of safety-oriented pre-check workflow.

## Production Improvements

Real production use would require additional engineering around the compact CLI shown here:

- vendor-specific parsers
- schema validation
- ticket-system integration
- CI/CD approval gates
- audit logs
- RBAC
- batch validation for many devices
- pre/post telemetry checks
- GitLab/Jenkins integration
