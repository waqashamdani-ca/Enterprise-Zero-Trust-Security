# Focused acceptance criteria and approval gates

**T6 baseline, 2026-11-06. Lab implementation PLANNED; operational tests NOT TESTED; owner user acceptance testing (UAT) PENDING.**

Engineering asks whether the approved lab works as specified. Owner UAT asks whether it supports the intended business workflows. Keep these decisions separate. [Assignment](../assignments/PROJECT-ASSIGNMENT.md) requirements and its single [100-point rubric](../assignments/PROJECT-ASSIGNMENT.md#success-criteria) govern this four-week baseline; no second rubric is defined here.

## Measurable completion criteria

All criteria below are mandatory for project engineering completion. Each FAC ID maps to the same-numbered FWR requirement, FSC control and FWT test in the [coverage index](TEST-PLAN.md#coverage-index).

| ID | Completion evidence |
| --- | --- |
| FAC-01 | Hardware readiness/approvals and isolation inspected; lab mock denial demonstrated; no protected-network probes/trust/data/credential reuse. |
| FAC-02 | One operational host/four baseline VMs, Management/Corporate/Restricted, capacity fit, named management/console recovery and actual permitted/default-denied flows. |
| FAC-03 | Separate AD/DNS/Group Policy; three standard users/role groups and one privileged admin; standard logon, all six role cases and app revocation verified. |
| FAC-04 | Supported Windows/Linux baseline, host firewalls, update/antivirus status and standard-user privilege denial verified. |
| FAC-05 | One CA/HTTPS leaf, correct chain/name/date behavior and untrusted-client rejection; trust restricted to lab clients. |
| FAC-06 | Separate lab Tailscale reaches only named APP1 HTTPS; unauthorized/wrong-port and existing/new revoked sessions denied; no broad routes or production enrollment. |
| FAC-07 | Five representative events from two or three relevant sources and one denied-access investigation tied to actual policy. |
| FAC-08 | One useful local operation, safe invalid-input rejection, correct output and repeat execution without unintended changes. |
| FAC-09 | One encrypted off-compute backup successfully restored in isolation; actual recovery time, data/HTTPS/role checks and exclusions recorded. |
| FAC-10 | All ten tests/every mandatory subcheck have evidence and PASS; no unresolved critical/high safety issue; five T7 final submissions and reviewed sanitized GitHub publication exist. |

A missing/blocked mandatory subcheck is NOT TESTED, not a pass or an approved omission. No 95% threshold, enterprise RPO/RTO, six-zone requirement, extra provider, two-tier CA, twenty-event target or extended retention calculation applies. Reintroducing enterprise scope requires explicit owner approval and corresponding specification changes before evaluation.

Critical isolation, privilege/authorization, TLS trust, remote exposure, recovery-integrity, secret-disclosure or false-result failures block acceptance regardless of points. Retain original failure evidence and record bounded remediation/retest. Scope changes require a new explicit owner decision; never downgrade an expected denial after seeing a permit.

## Phase gates and stage approvals

[AGENTS.md](../../AGENTS.md) still requires explicit approval **before every stage A-L**, identifying scope/assets/permitted changes/validation/rollback. The guide groups them into five phases, with stage L's explicitly approved automation/recovery portion before final K validation if needed. A document, PR merge or previous stage does not approve execution.

| Phase | Required exit evidence |
| --- | --- |
| 1: Infrastructure and Network | Delivered/inspected compatible assets where needed, data/service inventory, exact disk/backup/recovery approval, isolated host/firewall/three-zone policy and console recovery |
| 2: Identity and Endpoint Security | Directory counts/logon/policy, Windows/Linux host baseline and separate privileges |
| 3: Zero Trust Access Controls | Six app cases/revocation, one CA/leaf trust/expiry, one-resource Tailscale permit/deny/revoke |
| 4: Monitoring, Automation and Recovery | Five events/investigation, one repeatable operation and measured isolated APP1 restore |
| 5: Validation and Final Submission | Every test/subcheck passes, actual evidence/rubric, five T7 files, reviewed publication and separate owner UAT decision |

Delivery/compatibility, exact disk/recovery, safe egress and lawful software/provider terms are prerequisites, not results supplied by T6. Existing service migration/shutdown and destructive recovery need their exact owner scope. A temporary isolated APP1 restore copy is justified solely for FAC-09; it adds no permanent baseline VM.

## Engineering verification record

Record stage/approval/date, versions/asset roles, change, requirement/control/test/FAC IDs, expected and actual result, evidence reference, verifier, second observation, defects/severity, recovery state and verdict. A second tool/log observation is not independent human review. Retain actual operational fields empty until execution; current test verdicts stay NOT TESTED.

T6 engineering completion is narrower: consistent reviewed specifications/PDFs, focused regression and preservation checks, a finalized Markdown-only T6 report, actual CI/merge and local/remote synchronization. It does not require future T7 templates or operational tests to be performed. Historical bootstrap B01-B14 and earlier stage criteria are preserved in previous Git revisions/reports; they are not extra current implementation targets.

## Owner UAT record

The owner later checks analyst report access, engineer maintenance-page access, unassigned-user denial, remote access/revocation and understandable recovery/evidence records. Record reviewer/date, observed usability, limitations, follow-ups and explicit confirmation reference. **Owner UAT remains PENDING** without that confirmation. Engineering verification, grading, CI and publication cannot supply acceptance.

## Current gate

T6 is documentation only. No hardware/software installation, VM/network/directory change, Tailscale enrollment or lab/security-test execution is authorized. T7 requires separate approval to migrate the eight unchanged Office shells into the five planned files. See [task reports](../reports/INDEX.md) for observed results; the [project final report](../final-report/FINAL-REPORT.md) remains a template.
