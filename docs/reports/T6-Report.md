# T6 - Four-week focused lab specification alignment

Report state: DRAFT

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T6 |
| Execution date | 2026-11-06, America/Toronto |
| Authority | Owner T6 Four-Week Lab Scope Optimization request; Hardware Procurement Status addendum; Complete Project Specification Alignment addendum, all received 2026-11-06. Private originals retained by owner |
| Authorized scope | Align all active core specifications, necessary navigation/build/validation and generated PDFs; preserve eight Office files and finalized history; report, publish by PR, verify CI, merge and synchronize |
| Scope clarification | The complete-alignment addendum superseded the earlier restriction to assignment/guide. It did not authorize T7 or infrastructure work |
| Dependency baseline | T5 FINALIZED; PR 6 merged; original local main, origin/main and live remote main b838c00bc7d4478251662fc2086059d38a2c7ffd; T5 final-head workflow 42190129206 successful |
| Work preservation | Five pre-existing archive-PDF deletions remain in the original checkout. A clean isolated worktree was pulled with --ff-only from main, then task/006-four-week-lab-scope created. No owner change was overwritten/staged |
| Tooling | Existing bundled Python 3.12.14, pinned documentation libraries and Poppler; existing local Mistune/Pygments dependencies used through PYTHONPATH. No installation |

The business outcome is a realistic plan for verifying access to a synthetic report/maintenance application within four working weeks. T6 delivers the specification, not a working security lab. Measurable documentation outcomes are one consistent three-zone/four-VM design, ten requirements/controls/tests/acceptance criteria, six app access cases, five exact planned T7 filenames, a 100-point rubric, correct hardware status, matched readable PDFs and preserved history.

Threats considered include accidental protected connectivity, overbroad overlay access, stale manual permissions, key/evidence disclosure, unsafe recovery and overstated results. The design, threat/control model, requirements, future tests and rollback are updated before any implementation. Documentation rollback is a normal reviewed revert of editable T6 changes while retaining frozen reports/evidence; no infrastructure recovery operation is needed.

## B. Implementation Summary

| Changed files / group | Result |
| --- | --- |
| [Assignment](../assignments/PROJECT-ASSIGNMENT.md) and adjacent PDF | Four-page business-facing assignment, ten FWR requirements, four-week plan, five planned T7 submissions and the sole rubric |
| [Implementation guide](../lab-guides/LAB-IMPLEMENTATION-GUIDE.md) and PDF | Five phases with prerequisites/tools/steps/results/verification/troubleshooting/rollback; separate A-L approvals retained; proposed target-labelled examples only |
| [Architecture](../architecture/ARCHITECTURE.md) and PDF | Reviewed vector diagram, Management/Corporate/Restricted, four VMs, FF-01 through FF-08, identity/overlay/log/backup boundaries and measured-readiness gates |
| [Security](../security/SECURITY-REQUIREMENTS.md), [tests](../testing/TEST-PLAN.md), [acceptance](../testing/ACCEPTANCE-CRITERIA.md) and PDFs | Ten FSC/FWT/FAC entries, empty operational actual/evidence fields, six app cases, mandatory subcheck evidence and separate owner UAT |
| [Decisions](../governance/DECISIONS.md) / [risks](../governance/RISKS.md) and PDFs | DEC-23 through DEC-26, CH-010 and revised mitigations; obsolete decision rows labelled SUPERSEDED; RK-21 manual-role drift and RK-22 schedule dependencies |
| [README](../../README.md), [library](../README.md), [glossary](../guides/GLOSSARY.md), [references](../governance/REFERENCES.md), [build guide](../governance/DOCUMENTATION-BUILD.md), [project-report template](../final-report/FINAL-REPORT.md) and PDFs | Necessary current-scope/navigation/terminology alignment; project report remains visibly a template; legacy Office shells labelled historical |
| [PDF builder](../../scripts/build_docs.py), [document validator](../../scripts/validate_docs.py), [Office validator](../../scripts/validate_office_templates.py) and their three test files | Five-phase/ten-ID/rubric/T7/traceability checks; topology/layout updates; legacy T5 plan pinned by commit and hash; fail-closed missing-history check |
| Generated manifest, [report index](INDEX.md), this report | Builder-generated source/PDF records; Markdown-only T6 navigation/reporting. No report PDF |

The current baseline has one Proxmox host and four VMs: OPNsense, DC1, WIN1 and APP1. Planning allocations total 20 GiB guest RAM/176 GiB disks; provisional host/media/guest/temporary-restore/free ledger is 336 GiB. These are not observed hardware results. One CA signs one HTTPS leaf. One-resource Tailscale uses separate identities and explicit vendor plus effective host policy. Three sources supply five planned events, one denial investigation, one useful local capacity operation and one isolated APP1 restore. A temporary disconnected recovery copy exists only in the future restore procedure, not as a permanent extra VM.

The guide preserves every old R01-R16/T00-T20 mapping. Six zones become three; six standard/two privileged users become three/one; twelve app cases become six plus revocation; dual remote pilots become Tailscale only; two-tier CA/certificate-revocation service becomes one CA/basic HTTPS trust/expiry; six sources/twenty-event timing/extended retention become two or three sources/five events/investigation; two automations become one; enterprise RPO/RTO becomes measured application restore with explicit exclusions. HA/clustering remain excluded. Old evidence/IDs are not relabelled or reused for changed meanings.

The approved rubric is Infrastructure and Network Security 25; Identity and Access Controls 25; Security Monitoring and Operations 20; Testing and Recovery 20; Documentation and Final Submission 10. Plans earn no implementation credit; critical safety failures block acceptance.

Hardware correction: existing resources remain owner-reported and uninspected. Xeon W-2145, Samsung 1 TB SSD, Sabrent PCIe adapter, Intel I350-T4 NIC, GL.iNet Beryl AX and TP-Link managed switch are **Ordered**, per the latest accessible Technical Setup procurement discussion and owner's T6 correction. Expected November 7 non-CPU/November 12 CPU delivery dates are not receipts. Delivered is unconfirmed; installed/validated lab evidence absent. No reorder or scope expansion. Delivery/physical inspection/compatibility/current data-service inventory/backup-recovery/exact destructive approval precede installation; preserve original Windows disk/services.

DEC-25 records a simplification explicitly: Apache local hashed identities/roles mirror the three AD personas manually using distinct passwords. No automatic AD SSO/synchronization is claimed. App role removal and actual denial, not just an AD change, demonstrate revocation. Certificate-revocation infrastructure and AD/CA/host disaster recovery are excluded; app/device revocation and one APP1 restore remain mandatory.

## C. Testing and Validation

The engineering verifier was Codex. Second observations below were performed by the same verifier, not a separate reviewer. Public sources/code/PDFs and eventual hosted CI are reviewable evidence; raw local logs/previews/private procurement conversation remain outside publication.

| Executed check / expected outcome | Actual observation / evidence | Verdict |
| --- | --- | --- |
| Preflight Git/status/remotes/branches/T5/identity/rules | T5 report FINALIZED, PR 6 merged, final-head CI success and baseline SHA equality; public/main/admin-push metadata confirmed; five owner deletions isolated | PASS |
| Existing documentation toolchain version inspection | All six pinned packages match requirements-docs.txt using existing bundled runtime/local parser packages; no install | PASS |
| python scripts/build_docs.py | 19 maintained pairs, 78 pages; assignment 4 pages, guide 15; 14 changed PDFs regenerated from source; all reports excluded | PASS |
| python scripts/build_docs.py --check --rebuild-check | Fresh in-memory bytes match every PDF; source/text/navigation/link/metadata structure checked; minimum source-token coverage 1.0 | PASS |
| No-change build plus independent hash/mtime snapshot | All 24 maintained/archived PDF hashes and modification timestamps unchanged; builder reports 19 unchanged pairs | PASS |
| python scripts/validate_docs.py | 80 public candidate files/36 Markdown files; phase/traceability/rubric/links/workflow/report/migration/publication checks pass | PASS |
| python scripts/validate_office_templates.py | Eight legacy XML-only packages/30 worksheets retain old R01-R16/T00-T20 blank-shell contract, no actual/evidence/UAT fabrication | PASS |
| python -m unittest discover -s tests -v | 58 focused tests pass, including invalid links/secrets/Office packages, missing legacy history, wrong weights/IDs/fields/mappings/future filenames and frozen-history checks | PASS |
| Independent baseline SHA-256 comparison | 25 Office/report/archive/evidence files byte-identical to pre-T6 baseline; all eight Office files also compared directly to committed T5 bytes | PASS |
| Poppler rendering and manual visual review | All pages of 14 changed PDFs rendered; title/contents/tables/diagram/commands/transitions reviewed; refined pages re-rendered. No remaining clipping/overlap/unreadable content observed | PASS |
| git diff --check | No whitespace errors | PASS |
| --require-finalized completion gate | Pending until this report is finalized at an observed evidence cutoff | NOT TESTED |
| Operational FWT-01 through FWT-10, implementation approvals and owner UAT | No lab action performed; actual/evidence placeholders empty; none of these repository checks supplies an operational verdict | NOT TESTED |

Initial failures were retained privately and resolved: the first run encountered Windows-sandbox fixture access/cleanup errors and a five-page assignment. The same fixture tests ran normally under the approved unsandboxed documentation-only scope; a compact title/contents layout met four pages. A subsequent legacy-plan drift negative test exposed that the old Office checker silently parsed zero definitions from the new plan. It now reads the committed T5 plan at b838c00bc7d4478251662fc2086059d38a2c7ffd, verifies SHA-256 c01a987e29cfcfe637d5f25bbdbd8fecef526ae8175c0a6f9f3b604063e27811, requires all 21 old definitions and fails closed on missing history. No scanner was disabled. Code slice notation that resembled IPv6 literals was rewritten to remove the false finding.

Visual review corrected a split risk row, a narrow capacity column and an orphaned hardware line. Poppler emitted Symbol/ArialUnicode display-font warnings on some outputs; reviewed pages rendered legibly with the embedded document fonts. Text extraction was used for content/link checks, not as a substitute for visual layout inspection.

Primary vendor research supports proposed syntax/design. Direct Proxmox HTML returned 403 and one Microsoft direct fetch failed; official source/download and Microsoft indexed guidance provided the documented fallback. Exact installed-version commands, package paths, compatibility and runtime behavior remain future approval/validation dependencies. T6 executed no implementation example.

## D. Security and Quality Review

The complete proposed set, filenames, code/source content, PDF text/structure and current diff were manually reviewed alongside the bounded scanner. All public examples use reserved lab names/symbolic addresses; no secrets, actual internal addresses, private inventories, procurement order IDs, raw logs, backup/key material or corporate data were added. Existing authentication/remote URLs remain supported secure forms. No license, ruleset, reviewer setting, workflow privilege or account privacy setting changed.

Frozen reports/archives/evidence and all Office files retain their bytes. Report/index PDFs were not generated. Existing compatibility links resolve. Lab/test actuals remain blank, project final report remains a template, and no production/security improvement or independent reviewer/owner acceptance is claimed.

Residual risks are documented in the current risk register: delivery/compatibility and exact disk readiness, original data/services, safe egress, lawful software/provider features, manual app-role drift, one-host outage, limited certificate/recovery/monitoring coverage, public scanner limits and pending T7 migration. No risk acceptance is inferred.

## E. GitHub Operations

Authenticated user waqashamdani-ca has push/admin permission to the existing public repository, default main. Origin retains the authorized URL/case-insensitive repository match. main has no protection and rulesets are empty at preflight; settings unchanged. Both new author/committer identities were verified as the owner's GitHub noreply identity.

Branch: task/006-four-week-lab-scope. Baseline: b838c00bc7d4478251662fc2086059d38a2c7ffd. At this draft cutoff, the T6 content commit, push, PR, CI and merge are pending. Publication uses explicit paths and normal non-force Git updates. A future finalization records only outcomes already observed; later final-head CI/merge/synchronization belong in the final chat response.

## F. Outstanding Issues

T7 must migrate the eight unchanged Office shells into the five approved exact filenames and new IDs/rubric. Those future files are deliberately not created. Final lab submission cannot pass until separately authorized T7 and implementation/evidence exist.

Delivery, physical inspection, compatibility/cooler/firmware, current data/service inventory, off-compute recovery media, exact destructive targets, isolated egress, current software/provider terms and individual stage approvals remain pending. The four-week estimate starts after prerequisites and may move without weakening safety. The original checkout still has five owner PDF deletions and must not be described as clean. Independent human review NOT TESTED; owner UAT PENDING.

## G. Completion Status

| Area | State |
| --- | --- |
| T6 documentation and local engineering verification | IMPLEMENTED / VALIDATED for the checks above; report/publication in progress |
| Independent second observations | PASS for PDF render/content, byte preservation and GitHub preflight methods; same engineering verifier |
| Independent human review | NOT TESTED |
| Report / publication | DRAFT; initial publication and finalized completion gate pending |
| Lab hardware/software/controls | PLANNED / NOT TESTED; no implementation action |
| Owner UAT / acceptance | PENDING; no explicit confirmation received |

## H. Next Task

Recommend **T7 only**: migrate/consolidate the eight legacy Office shells into the five approved submission templates. Require explicit owner approval of exact filenames, preservation/replacement rules, FWR/FWT/FSC/FAC/rubric mappings, native/visual/formula validation and rollback before execution. No infrastructure work is included. Stop after T6 publication/synchronization and await owner review.
