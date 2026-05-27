# Rollback Checklist

Use this checklist before implementing a configuration change that has high or critical validation findings.

## Pre-change
- Current configuration exported and stored with timestamp: No
- Backup location verified by second engineer: No
- Maintenance window confirmed with operations: No
- Rollback owner assigned: No
- Service health baseline captured: No
- Remote recovery access confirmed: No
- Stakeholders informed of rollback trigger conditions: No

## Rollback Triggers
- Management or recovery access is lost.
- Default gateway or routing validation fails after implementation.
- RAN neighbor relation counters degrade beyond the accepted threshold.
- Controller redundancy does not return to expected state.
- Any critical alarm remains active after the agreed observation period.

## Rollback Actions
1. Stop further planned changes in the batch.
2. Restore the pre-change configuration snapshot.
3. Verify management access and service reachability.
4. Confirm alarms, routing, synchronization, and controller state.
5. Record final status in the change report.

## Post-rollback
- Incident or change record updated: No
- Root cause documented: No
- Follow-up validation rules updated if needed: No
