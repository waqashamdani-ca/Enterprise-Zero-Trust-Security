# Decision register and change history

**Implementation status: NOT STARTED.** "Proposed" records a design recommendation, not owner authorization to implement. Each stage still needs separate explicit approval under [AGENTS.md](../AGENTS.md).

## Decision register

| ID | Decision / rationale | Status and owner | Revisit trigger |
| --- | --- | --- | --- |
| DEC-01 | Task 001 covers planning, repository scaffold, documentation validation, and reviewed public Git publication only | Authorized by owner task and addendum; technical lead executes | Any request to install, deploy, configure, or test the lab |
| DEC-02 | Prefer a single verified Dell host with private virtual bridges and virtual OPNsense; no cluster/HA claim | Proposed; owner approves after Stage A | Hardware/disk/CPU incompatibility, insufficient capacity, or inability to dedicate host |
| DEC-03 | Offline baseline first; independent protected-network isolation required before any uplink. A WAN NIC on the home LAN alone is insufficient | OPEN / BLOCKING online stages; owner + architect | Concrete inspected cable/interface/egress boundary and rollback available |
| DEC-04 | Public docs use symbolic address labels and `ad.lab.test`; actual addresses/protected aliases stay outside Git | Proposed design; private inventory/address choice OPEN; architect | Overlap with existing home/production/overlay ranges or naming incompatibility |
| DEC-05 | Select supported Proxmox/OPNsense/Windows/Linux versions at stage entry; use lawful evaluation terms and record deadlines | OPEN; owner + engineer | Stage A/B media and compatibility review; no software assumed installed |
| DEC-06 | Separate offline standalone root and online issuing CA; no lab root trust outside lab | Proposed; owner approves Stage G design/key custody | Capacity/skills/lifecycle constraints; any simplification requires revised R07 acceptance |
| DEC-07 | Start with WEC and Linux/syslog collection; no heavyweight SIEM assumed | Proposed; log transport/source exports/retention capacity OPEN; engineer | Measured event volume, unsupported source transport, or remote-plan export limitations |
| DEC-08 | Encrypted off-compute supported backups; proposed representative recovery RPO 24h/RTO 4h | OPEN / BLOCKING recovery claim; owner | Verified backup capacity/device, key custody, identity/CA scope, and supported restore method |
| DEC-09 | Evaluate Tailscale/Twingate sequentially with separate lab-only identities/environments and one resource per pilot | Proposed; identity/provider plan/MFA/recovery choices OPEN; owner | Stage I entry; auto-enrollment risk, paid-plan dependency, unavailable logging/posture |
| DEC-10 | Do not select a license in bootstrap | Deferred pending explicit owner choice | Owner approves license/rights and scope of reuse |
| DEC-11 | Public repository under `waqashamdani-ca`, `main`, intentional reviewed commits; task branches and PRs after initial bootstrap | Authorized by owner addendum; repository engineer | Existing remote work, permission conflict, repository policy change |
| DEC-12 | Repository rulesets/required checks/reviewers are not changed silently; documented PR conventions are initially procedural | OPEN; owner | Owner selects enforceable rules and available reviewer model |
| DEC-13 | Stage A is a read-only readiness assessment; Stage B contains destructive disk installation | Planning baseline; owner approval for either execution remains PENDING | Owner issues a stage-specific scope/approval |
| DEC-14 | Every task has a sequential A–H report in `reports/`; finalized records are immutable and corrections use separate addenda; project-level final report remains a template | Authorized by owner reporting-governance addendum | A later owner-approved reporting change; historical finalized content remains preserved |

Do not treat hardware descriptions, planning allocations, or documented software alternatives as an inspected fact or an implemented choice. Resolve each blocking decision before its dependent stage.

## Approval and change record format

For each later decision/change, record ID, date, problem/trigger, options, selected outcome, rationale, affected requirements/tests/artifacts, security/production impact, rollback, engineering verifier, owner approval reference, and status. Never paste private chat transcripts, actual addresses, or secrets. Use an opaque approval reference with the private record retained by the owner.

## Bootstrap change history

| Change | Date | Scope and authority | Effect |
| --- | --- | --- | --- |
| CH-001 | 2026-11-05 | Owner Task 001 | Establish assignment, proposed architecture/guide, security and acceptance framework, public-safe scaffold and documentation checks; no implementation |
| CH-002 | 2026-11-05 | Owner GitHub integration/synchronization addendum | Confirm exact account/repository/public visibility, secure existing authentication, controlled commits/PRs/pulls, `main`, CI and local/remote verification; prohibit background sync |
| CH-003 | 2026-11-05 | Task 001 completion verification within the existing authorization | Public bootstrap pushed with existing Git Credential Manager login; initial documentation CI and local/remote synchronization verified; add sanitized completion evidence without starting a lab stage |
| CH-004 | 2026-11-05 | Owner task-reporting governance addendum | Migrate the original Task 001 report with a verbatim source appendix, establish sequential immutable reports and focused checks, and separate individual reports from the project-level final template |

Actual Task 001 commit IDs and CI/publication evidence are recorded in [T1-Report.md](../reports/T1-Report.md) and its addenda. Each later task records its own results in [reports/](../reports/README.md). [FINAL-REPORT.md](FINAL-REPORT.md) is the project-level template. No implementation stage approval or owner UAT decision has been recorded.
