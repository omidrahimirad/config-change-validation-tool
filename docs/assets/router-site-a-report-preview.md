# Configuration Change Validation Report

## Change Summary
- Device/System: RTR-SITE-A-01
- Environment: production
- Changed fields: 6
- Validation status: Failed
- Risk level: High Risk
- Final decision: Requires senior approval

## Detected Changes
| Field                        | Current Value                  | Planned Value                  | Risk     |
|:-----------------------------|:-------------------------------|:-------------------------------|:---------|
| interfaces.uplink.ip_address | 172.16.10.2/24                 | 172.16.20.2/24                 | Low      |
| interfaces.uplink.mtu        | 1500                           | 1600                           | Low      |
| interfaces.uplink.vlan       | 210                            | 211                            | Low      |
| management_ip                | 10.42.10.10                    | 10.42.10.20                    | Critical |
| ntp.servers                  | `['10.42.1.10', '10.42.1.11']` | `[]`                           | Medium   |
| static_routes                | Route table changed            | Route table changed            | Low      |

## Failed Validation Rules
| Rule ID | Severity | Description                                           | Finding                                                                     |
|:--------|:---------|:------------------------------------------------------|:----------------------------------------------------------------------------|
| NET-001 | Critical | Management IP must not change without approval.       | management_ip changed from '10.42.10.10' to '10.42.10.20' without approval. |
| NET-003 | High     | Default gateway must be reachable in the same subnet. | Default gateway 172.16.10.1 is not reachable within 172.16.20.0/24.         |
| NET-006 | Medium   | NTP server list must not be empty.                    | ntp.servers must not be empty.                                              |

## Risk Score
- Total score: 75
- Risk level: High Risk

## Approval Checklist
- Backup confirmed: Yes
- Maintenance window defined: Yes
- Rollback plan available: Yes
- Peer review completed: No
- Senior approval required: Yes

## Rollback Recommendation
Block implementation until critical findings are resolved. Confirm backup status, document restoration steps, and rehearse the rollback trigger before scheduling the change.
