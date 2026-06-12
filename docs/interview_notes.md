# Interview Notes

This document is a preparation aid for technical interviews. It explains the engineering choices behind the project in concise terms.

## Why this project was built

The project models a repeatable way to review planned configuration changes before implementation. It is based on the kind of checks engineers perform during change windows: preserving recovery access, verifying routing consistency, confirming backup readiness, and documenting rollback conditions.

## Problem being solved

Configuration files can be syntactically valid while still introducing operational risk. The tool compares current and planned configurations, evaluates the planned state against explicit rules, and produces a report that can support a change-review discussion.

## Architecture decisions

The project uses a small pipeline:

1. Load current and planned YAML configuration files.
2. Compute field-level differences.
3. Evaluate YAML-defined validation rules.
4. Score failed checks by severity.
5. Generate a Markdown report with decision, checklist, and rollback recommendation.

The modules are separated by responsibility so the parser, diff engine, rule engine, risk scoring, reporting, and CLI can be tested independently.

## Why YAML rules

YAML keeps validation rules readable for reviewers who may not be Python developers. It also separates operational policy from the rule engine implementation. For this portfolio project, that separation is more useful than embedding every check directly in Python.

## Why not use a database

The project validates file-based examples and does not need persistent state. A database would add setup cost without improving the core validation workflow. If the tool managed historical changes, approvals, or inventory across many systems, a database would become more appropriate.

## Why not build a web application

The core value is the validation workflow, not the interface. A CLI is easier to run in CI, easier to test, and closer to how infrastructure validation tools are often used in scripted change processes. A web UI could be added later, but it would not change the core rule and risk logic.

## Risk-scoring design

Risk scoring is intentionally deterministic and simple:

- critical = 40 points
- high = 25 points
- medium = 10 points
- low = 5 points

This makes the decision path easy to explain. In a real environment, weights would likely be adjusted by service criticality, maintenance window, redundancy, customer impact, and operational policy.

## Known limitations

The project uses synthetic YAML configuration data and simplified validation rules. It does not connect to live devices, execute configuration changes, enforce approvals, or perform transactional rollback. Vendor-native parsers, authentication, audit trails, and large-scale inventory handling are outside the current scope.

## Production improvements

Reasonable production-oriented extensions would include:

- Vendor-specific parsers for real configuration formats.
- Stronger schema validation per domain.
- Integration with change records or approval systems.
- Role-based access control and audit logging.
- Historical configuration snapshots and drift detection.
- Environment-specific risk weighting.
- Safer handling of sensitive configuration values.

## Scaling considerations

For larger inventories, the tool would need batch execution, result aggregation, parallel validation, consistent naming conventions, and a durable store for historical reports. Rule ownership and versioning would also become important so operational policy changes can be reviewed.

## Telecom/infrastructure relevance

The examples reflect common infrastructure review concerns: management access, gateway reachability, MTU limits, SSH recovery access, RAN PCI/TAC constraints, neighbor cell readiness, backup confirmation, maintenance windows, and rollback planning.

## Lessons learned

Good validation tooling is not only about parsing files. The useful engineering work is making operational assumptions explicit, translating review logic into repeatable checks, and producing reports that help people make safer implementation decisions.
