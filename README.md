# Configuration Change Validation Tool

A Python-based validation tool for comparing current and planned configuration files, checking the planned change against YAML-defined engineering rules, scoring operational risk, and generating a Markdown change report with approval and rollback guidance.

The project is designed as a professional portfolio artifact for roles involving telecom, railway infrastructure, industrial networks, system integration, and change management. It uses synthetic configuration data and deliberately simplified rules so the workflow is easy to inspect and test.

## Why This Project Exists

Manual configuration reviews often rely on repeated checks: has recovery access been preserved, are gateway and subnet changes consistent, is a rollback plan documented, and does the change need senior approval? In large change windows, hundreds of parameters may be reviewed by hand. This project turns that review pattern into a reproducible CLI workflow.

## Problem Statement

Configuration changes can be technically valid YAML while still being operationally risky. A planned file may parse correctly but remove NTP, change a management address without approval, break gateway reachability, or miss a maintenance window. The goal is to detect those risks before implementation and produce a report that is useful in a change-review conversation.

## Architecture

```text
Current config
  -> Planned config
  -> Validation rules
  -> Parser
  -> Diff engine
  -> Rule engine
  -> Risk scoring
  -> Markdown report
  -> Approval checklist
  -> Rollback recommendation
```

## Features

- YAML-based current and planned configuration parsing
- Recursive diff engine for nested configuration fields
- Rule files stored in YAML rather than hardcoded into one script
- Validation categories for schema, safety, network consistency, change risk, operational readiness, and rollback
- Risk score and approval decision mapping
- Markdown report generation with change tables and rule results
- uv-native dependency management with `pyproject.toml` and `uv.lock`
- CLI entry points using `uv run python -m change_validator` and `uv run change-validator`
- Synthetic examples for network, RAN-like, and industrial controller domains
- Pytest coverage and GitHub Actions CI

## Example Configuration Domains

Network configuration:
- `device_id`, `site`, `device_type`, `management_ip`
- Interfaces with VLAN, MTU, and IP address
- Default gateway and static routes
- SSH, SNMP, and NTP settings

Telecom / RAN-like configuration:
- `cell_id`, `site`, `band`, `pci`, `tac`
- `max_tx_power_dbm`, `handover_margin_db`
- Neighbor cell list

System / industrial controller configuration:
- `system_id`, `environment`, redundancy settings
- Backup requirement and maintenance window
- Logging level and rollback plan

## Validation Rule Examples

Network rules:
- `NET-001`: Management IP must not change without approval. Severity: critical.
- `NET-002`: MTU must stay between 1280 and 9000. Severity: high.
- `NET-003`: Default gateway must be reachable in the same subnet. Severity: high.
- `NET-004`: SSH must remain enabled for remote recovery. Severity: critical.

RAN rules:
- `RAN-001`: PCI must be between 0 and 1007. Severity: critical.
- `RAN-002`: TX power change above 3 dB requires high-risk approval. Severity: high.
- `RAN-003`: Neighbor cell list must not be empty. Severity: high.
- `RAN-004`: TAC change requires rollback plan. Severity: critical.

Operational/system rules:
- `OPS-001`: Production changes require a maintenance window. Severity: critical.
- `OPS-002`: Backup must be confirmed before change. Severity: critical.
- `OPS-003`: Rollback plan must exist for high-risk changes. Severity: critical.

Implemented check types:
- `range`
- `must_equal`
- `not_empty`
- `max_delta`
- `no_change_without_approval`
- `subnet_consistency`
- `required_if_environment_production`
- `requires_rollback_plan`
- `required_if_risk_high`

## Risk Scoring Logic

Severity points:
- critical = 40 points
- high = 25 points
- medium = 10 points
- low = 5 points

Risk levels:
- 0-20 = Low Risk
- 21-50 = Medium Risk
- 51-90 = High Risk
- 90+ = Critical Risk

Approval decision:
- Low Risk -> Approved
- Medium Risk -> Approved with review
- High Risk -> Requires senior approval
- Critical Risk -> Rejected / blocked

## CLI Usage

Install uv if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create the project environment from `pyproject.toml` and `uv.lock`:

```bash
uv sync
```

Run the network validation example:

```bash
uv run python -m change_validator validate \
  --current configs/current/router_site_a.yaml \
  --planned configs/planned/router_site_a.yaml \
  --rules rules/network_rules.yaml \
  --output reports/router_site_a_change_report.md
```

The console script is also available through uv:

```bash
uv run change-validator validate \
  --current configs/current/router_site_a.yaml \
  --planned configs/planned/router_site_a.yaml \
  --rules rules/network_rules.yaml \
  --output reports/router_site_a_change_report.md
```

## Sample Terminal Output

```text
Validation completed.

Changed fields: 6
Passed checks: 14
Failed checks: 3
Risk score: 75
Risk level: HIGH
Decision: REQUIRES SENIOR APPROVAL

Report saved to:
reports/router_site_a_change_report.md
```

## Sample Failed Validation Explanation

The sample router change fails because the management IP changes without approval, the planned gateway is no longer reachable from the planned uplink subnet, and the NTP server list is empty. These are not syntax errors; they are operational risks that could affect recovery access, routing reachability, and event correlation during an incident.

Failed example report: `examples/failed_change_example.md`

## Sample Approved Validation Explanation

The sample RAN change adjusts PCI, handover margin, TX power, and neighbor relations while staying inside the defined validation limits. It keeps the neighbor list populated, maintains backup and maintenance-window readiness, and has an available rollback plan.

Approved example report: `examples/approved_change_example.md`

## Example Markdown Report Preview

```markdown
# Configuration Change Validation Report

## Change Summary
- Device/System: RTR-SITE-A-01
- Environment: production
- Changed fields: 6
- Validation status: Failed
- Risk level: High Risk
- Final decision: Requires senior approval

## Failed Validation Rules
| Rule ID | Severity | Description | Finding |
|---|---|---|---|
| NET-001 | Critical | Management IP must not change without approval. | management_ip changed without approval. |
| NET-003 | High | Default gateway must be reachable in the same subnet. | Gateway is outside the planned uplink subnet. |
```

Full sample report: `reports/sample_change_report.md`

## Test and CI Instructions

Run tests locally:

```bash
uv run pytest -v
```

The GitHub Actions workflow in `.github/workflows/ci.yml` installs uv, syncs dependencies from `uv.lock`, runs `uv run pytest -v`, and performs CLI smoke tests on every push and pull request.

Generate the included sample reports:

```bash
uv run change-validator validate \
  --current configs/current/router_site_a.yaml \
  --planned configs/planned/router_site_a.yaml \
  --rules rules/network_rules.yaml \
  --output reports/router_site_a_change_report.md

uv run change-validator validate \
  --current configs/current/ran_cell_001.yaml \
  --planned configs/planned/ran_cell_001.yaml \
  --rules rules/ran_rules.yaml \
  --output reports/ran_cell_001_change_report.md

uv run change-validator validate \
  --current configs/current/controller_01.yaml \
  --planned configs/planned/controller_01.yaml \
  --rules rules/system_rules.yaml \
  --output reports/controller_01_change_report.md
```

## Engineering relevance

“This project demonstrates how manual configuration review logic can be translated into a reproducible validation workflow. The focus is not only on parsing files, but on identifying operational risks before implementation: recovery access, rollback readiness, maintenance-window discipline, parameter consistency, and approval requirements.”

This is relevant to engineering work where configuration changes need to be reviewed consistently, documented clearly, and approved based on operational impact rather than file syntax alone.

## German Keywords

- Konfigurationsvalidierung
- Change Management
- Qualitätssicherung
- Systemintegration
- Fehlervermeidung
- Rollback-Planung
- Netzwerkbetrieb
- Technische Dokumentation

## Limitations

- The rules are simplified and synthetic.
- The tool does not connect to live devices, OSS platforms, industrial controllers, ticketing systems, or CI/CD deployment pipelines.
- Schema validation is intentionally lightweight and rule-driven instead of using a full JSON Schema model.
- Risk scoring is deterministic and transparent, but real environments may require service-specific weighting and approval policies.

## Future Improvements

- Add JSON input support alongside YAML.
- Add stricter schema validation for each domain.
- Add rule tags for change windows, technology owner, and approval group.
- Export reports to HTML or PDF.
- Add batch validation for a folder of planned changes.
- Add baseline health checks from synthetic pre/post-change telemetry files.

## Disclaimer

“This project uses synthetic configuration data and simplified validation rules. It is inspired by real production change-control workflows, but it is not connected to any live operator, railway, or industrial system.”
