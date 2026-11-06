# Acceptance criteria and approval gates

Acceptance answers two different questions: did the engineer verify the approved work, and did the owner accept it for its intended use? Keep those decisions separate. Repository/documentation checks have evidence in the [task reports](../reports/README.md); lab implementation is PLANNED and its operational controls are NOT TESTED.

The criteria below define what evidence a reviewer needs. A passing continuous integration (CI) run checks the repository; owner user acceptance testing (UAT) needs explicit confirmation. See the [glossary](GLOSSARY.md) for these terms.

## Task 001 bootstrap criteria

| ID | Criterion | Verification |
| --- | --- | --- |
| B01 | Preserve existing work, inspect tooling/authentication/target repository, and resolve conflicts before mutation | Preflight report and Git/remote inspection |
| B02 | Create every requested file/directory with useful content or a clearly scoped future-use README | Required-structure validator and Git tree |
| B03 | Assignment covers scenario, business case, measurable requirements, scope, dependencies, architecture, threats, standards, deliverables, tests, 100-point rubric, publication, and honest achievement objectives | Validator anchors/rubric plus independent content review |
| B04 | Guide covers A–L with prerequisites, procedures, proposed commands, expected outcome, verification, rollback, and completion criteria for every stage | Stage-section validator plus manual feasibility review |
| B05 | Architecture protects home/production, defaults deny, addresses management/egress/DNS/IPv6/secrets/logging, and flags unverified hardware/resources | Cross-document review; no operational test claim |
| B06 | AGENTS.md contains stage approval, documentation-first, bounded work, production/destructive restrictions, public hygiene, verification/UAT separation, tracking, and controlled Git workflow | Governance review |
| B07 | All local Markdown destinations/anchors resolve; required IDs are traceable; focused validator tests and whitespace checks pass | Local checks and hosted CI |
| B08 | Proposed published contents and history contain no detected secrets, actual internal addresses, sensitive exports, or proprietary source, and receive manual public-safety review | T00/T17; acknowledge pattern-scan limits |
| B09 | Authorized public GitHub repository uses `main`; official checkout action is commit-pinned, token is read-only, credentials are not persisted, and documentation-only CI passes | GitHub metadata and actual Actions run |
| B10 | `origin` is correct, local `main` tracks remote `main`, status is clean, and local/remote SHA match; report URL/user/branch/SHA/CI/blockers | Required Git synchronization commands and remote read-back |
| B11 | No software install, VM creation, infrastructure/network/identity change, or security-test execution occurred; stop after Task 001 | Executed-action review and explicit completion report |
| B12 | Open decisions/risks and one recommended next task are reported; owner UAT is not inferred | Final report; owner review remains pending |
| B13 | Every completed task has a unique sequential finalized A–H report in `reports/`; historical finalized reports are preserved | Reporting validator, source comparison, Git history review |

If GitHub authentication/permissions block publication, B09/B10 remain blocked and the local reviewed repository plus precise owner action are delivered. Do not present a local-only repository as published. If the target already exists, preserve and reconcile its branches/content without force-pushing.

## Future stage acceptance

Obtain scope-specific owner approval **before each stage**. To finish a stage, record engineering checks, reviewed evidence, unresolved issues, and the owner's separate acceptance decision. Finishing one stage does not authorize the next.

| Stage | Minimum exit evidence | Blocking condition |
| --- | --- | --- |
| A | Verified hardware/disk ownership, usable capacity, offline cable plan, backup/console feasibility, and go/no-go | Uncertain asset ownership or unverified destructive-install target |
| B | Supported isolated hypervisor, administrator/MFA, console recovery, patch/capacity record | Missing disk approval/backup or unmanaged protected-network connection |
| C | Six zone bridges, no ordinary guest uplink/host routing, reviewed IPv6 and console rollback | Shared physical/home bridge or unaccounted forwarding |
| D | Effective default-deny policy, management protection, scoped allows, mocked boundary verification | Broad LAN allow, protected path, exposed administration, unapproved egress |
| E | Separate lab forest/DNS/GPO, synthetic identities, recovery/evaluation deadlines | Production trust/sync/credentials or broken domain dependencies |
| F | Supported Windows/Linux endpoints, host firewall, standard/admin separation | Dual-homed guest, real corporate profile, or ordinary-user admin access |
| G | Offline root, separate issuer, scoped templates, valid/untrusted/revoked relying-application results | Exported CA key, broad enrollment, production trust, or unsupported revocation claim |
| H | Twelve role/resource cases, same-zone enforcement, measured revocation | Any unintended resource/admin access or unmet revocation target |
| I | Two separate sequential lab pilots, narrow resources, MFA/recovery, deny/revocation and route/DNS evidence | Corporate enrollment, wildcard access, subnet/exit exposure, or unresolved safe egress |
| J | Six sources, at least 19/20 timely events, clock target, retention design/health evidence | Missing source class, unsupported claimed export/encryption, or unbounded disk growth |
| K | Executed traceable cases, all critical passed, noncritical threshold met, no high-severity issue | Unexecuted mandatory cases, hidden failure, or unapproved test scope |
| L | Two bounded automations, repeat-run verification, encrypted off-compute timed restore, final evidence/report, owner UAT | Unproven recovery, unsupported claims, secret publication, or pending final owner acceptance |

An owner-approved scope exception must record affected requirements/tests, justification, risk, revised acceptance, and rubric impact before evaluation. Unavailable features remain a gap until that decision; do not silently lower targets.

## Engineering verification record

In the individual task report, identify the stage/branch, approval/date, actual versions and asset roles, changed files/configuration, requirement/test IDs, expected and actual results, evidence IDs, verifier and second observation, defects/severity, rollback readiness, and verdict. Mark missing tests NOT TESTED. A second tool or observation supports verification; it is not a second human reviewer unless someone else participated.

## Owner UAT record

Record the owner/reviewer, date, business workflows checked, observed usability, accepted limits, follow-up items, and explicit acceptance decision separately. Leave owner UAT pending until the owner supplies that decision. Engineering completion, GitHub publication, and CI do not supply owner acceptance.

## Current gate

Task 001 technical results are recorded in [T1-Report.md](../reports/T1-Report.md), its separately recorded addenda, and the final chat completion response. Every future task must finalize its own [individual report](../reports/README.md) before engineering completion. [FINAL-REPORT.md](FINAL-REPORT.md) remains the project-level template. Owner UAT: **PENDING**. Stages A–L: **NOT STARTED / NOT APPROVED FOR EXECUTION**. No next task starts without the owner's scope-specific authorization.
