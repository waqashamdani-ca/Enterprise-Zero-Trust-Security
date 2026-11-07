# T8 - Plain-English Lab Guide Rewrite and Instructional Redesign

Report state: DRAFT

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T8 |
| Execution date | 2026-11-07, America/Toronto |
| Evidence cutoff | DRAFT; finalization/publication observations will be recorded before this report is frozen |
| Authority | Owner T8 request and separate read-only reviewer-agent permission, 2026-11-07; originals retained privately |
| Authorized scope | Lab Guide rewrite/PDF redesign, necessary navigation/references, focused checks, Markdown-only report and reviewed GitHub synchronization |
| Dependency | T7 FINALIZED; PR 10 merged at df36c2a0495b83aa8036985d38de3d71a9242824; main workflow 42311527582 SUCCESS; local/tracking/live main agreed before changes |
| Branch | codex/008-plain-english-lab-guide; clean isolated worktree, git pull --ff-only origin main already up to date |
| Preservation | Original checkout has five pre-existing archive-PDF deletions; retained without staging, restoring or publishing them |
| Tools | Existing bundled Python 3.12.14, pinned documentation libraries, PowerShell parser, Git Bash syntax parser and Poppler; no software/fonts installed |

The owner needs a practical manual that explains unfamiliar software well enough to follow the approved four-week lab. The target is actionable instructions and readable evidence/recovery guidance, with the assignment, security controls, ten requirements/tests, rubric and Office files preserved. No hardware inspection, installation, VM/network/directory change, remote enrollment, lab exercise or Office-template edit is authorized.

Preflight read AGENTS, the assignment, guide, architecture, security requirements, tests/acceptance, all five Office packages, decisions/risks, reporting/build instructions and CI/regression system. Threats considered were unsafe copy/paste, ambiguous disks/targets, weakened boundaries, stale role/overlay access, leaked secrets and invented results. The validation plan combined source/specification review, official vendor references, focused regression/history checks, PDF structure/text checks, all-page visual review and a separate AI editorial reviewer. Rollback is a reviewed revert of editable T8 artifacts preserving finalized records, history and owner work.

## B. Implementation Summary

The guide is rebuilt around 27 numbered procedures within the same five phases. Each identifies purpose/location, ordered actions, expected/verification checks and failure recovery. Before starting, the reader has a short explanation of private values, stage approvals, version selection, file ownership and the five answer records.

| Before | After |
| --- | --- |
| A-H specification fields repeated for every phase; several independent operations compressed into one instruction | Practical steps with small actions, exact application locations/fields and phase checkpoints |
| Linux networking/firewall and service controls deferred to unspecified selected tools | Conditional Ubuntu/Netplan/nftables/systemd/Apache examples with files, activation, inspection and scoped recovery |
| Directory/group/policy tasks named without enough beginner detail | Installation choices, AD promotion, exact users/groups, DNS/domain join, domain-root password policy, separate DC audit policy and local policy/privilege checks |
| Certificate commands separated from explanation of trust and account roles | CA versus leaf explained, private paths/custody, before/after client trust, exact six authenticated cases and separate application/remote revocation |
| Monitoring/automation/restore summarized at a high level | Exact source views, five categories, one investigation, safe script rejection/repeat method, encrypted-mount guard, private manifest comparison and isolated restore/cleanup |
| Office filenames listed mainly at the end | References at the relevant procedures; all five names, 14 worksheets and 19 Word sections match actual packages |
| Historical migration tables and repository mechanics mixed into lab instructions | Exact tables preserved in a separate historical appendix; engineering mechanics linked to their authoritative instructions |

Jargon is explained when needed: virtual machine, bridge, AD, DNS, forest, OU, security group, Group Policy/GPO, certificate/CA/CSR/SAN/TLS, overlay/ACL and UTC. Reader-facing internal task language and report/branch mechanics are removed. This is a qualitative editorial assessment, not an invented readability score, observed beginner trial or owner acceptance result.

Changed paths are limited to 15 documentation/validation artifacts:

- [Lab Guide source](../lab-guides/LAB-IMPLEMENTATION-GUIDE.md) and adjacent PDF.
- [Historical mapping appendix](../governance/HISTORICAL-REQUIREMENT-TRANSITION.md) and adjacent PDF; both original transition tables retain their exact source text.
- [Test Plan](../testing/TEST-PLAN.md) and adjacent PDF: only two historical-navigation references/labels change; test methods, expected results and evidence fields are unchanged.
- [Documentation build guide](../governance/DOCUMENTATION-BUILD.md) and adjacent PDF: one layout-description sentence changes.
- [Report index](INDEX.md), this Markdown-only report and the generated [manifest](../documentation-manifest.json).
- scripts/build_docs.py, scripts/validate_docs.py, tests/test_build_docs.py and tests/test_validate_docs.py.

Guide-only rendering uses navy/gray headings, 10-point body text, 8.9-point table text and 8.8-point code, an uncluttered linked contents list, bookmarks/page numbers and intact filenames. Code blocks and their risk/target context stay together, each numbered action stays on a page, and tables repeat headers. The final guide has 41 pages and 45 named destinations. The other changed PDFs have 2 appendix, 3 build-guide and 8 Test Plan pages: 54 changed/new pages visually reviewed. No Office or report PDF was created.

No architectural decision, requirement, rubric, risk acceptance, license or repository setting changed. Conditional example profiles do not approve software versions/backends. Stage-entry values and approvals remain dependencies.

## C. Testing and Validation

All results below are documentation engineering observations on 2026-11-07. They are not operational FWT passes. Full private tool/fixture/preview records remain outside the public set.

| Check / actual command | Expected and actual result | Verdict |
| --- | --- | --- |
| T7 report, PR 10, workflow 42311527582; Git refs/live read-back | FINALIZED, merged, main CI SUCCESS, local/tracking/live df36c2a0495b83aa8036985d38de3d71a9242824 agree | PASS |
| python scripts/build_docs.py | 20 maintained pairs / 106 pages; only the three edited existing PDFs and one new appendix PDF differ from baseline | PASS |
| python scripts/build_docs.py --check --rebuild-check | All source/hash/text/navigation links match; deterministic fresh rendering agrees | PASS |
| python scripts/validate_docs.py | 84 public candidate files / 41 Markdown files; links, coverage, procedure context, hygiene, numbering and frozen history pass | PASS |
| python scripts/validate_office_templates.py | Five unchanged blank packages, 14 sheets, ten tests/91 child checks, approved outcomes, blank actuals/evidence, pending UAT and 100-point rubric | PASS |
| python -m unittest discover -s tests -v | 79 tests pass, including negative report/link/publication fixtures, core command preservation, appendix gaps, procedure fields/list boundaries, whole code/context/action pagination and Office checks | PASS |
| PowerShell Parser.ParseInput on seven fenced PowerShell blocks | Zero syntax errors; no block executed | PASS |
| Git Bash bash -n on 27 fenced shell blocks | Zero syntax errors; no block executed | PASS |
| Baseline Git blob comparison against df36c2a0495b83aa8036985d38de3d71a9242824 | 69 existing tracked files byte-identical, including all five Office files and 17 immutable report/archive files; assignment/architecture/security/acceptance/final-report/evidence unchanged | PASS |
| Exact historical-table and Office-label comparison | Both old tables preserved exactly; every actual filename/worksheet/section reference present | PASS |
| No-change build with before/after hashes and mtimes | All 25 current/archived public PDFs retain identical hashes/mtimes; 20 maintained outputs unchanged | PASS |
| Poppler rendering and manual image review | All 41 guide pages plus all 13 supporting changed/new PDF pages reviewed; title/contents/tables/code/links/footers and transitions readable, no clipping/overlap/missing glyph observed | PASS |
| Independent editorial read-through and correction read-back | Separate AI reviewer inspected the entire source and scope; final verdict PASS, no remaining substantive source finding | PASS |
| git diff --check; complete candidate/staged/history review | No whitespace finding; reviewed public-safe paths only; final publication read-back remains pending at this draft cutoff | PASS for local review |
| python scripts/validate_docs.py --require-finalized | Required after report finalization, before completed-task merge; not yet run at this draft cutoff | NOT TESTED |
| FWT-01 through FWT-10; hardware and lab procedures | No authorized operational execution in T8 | NOT TESTED |
| Independent human review / owner UAT | No independent human sign-off or explicit owner acceptance supplied | NOT TESTED / PENDING |

Commands used the existing pinned documentation environment; no dependencies were installed. Initial checks found a missing procedure recovery label, an outdated keyword/mutation fixture, and two Markdown paragraph/list boundaries; those were corrected. A visual pass found command context separated from its block; the renderer and regression now keep both together. Early temporary-fixture and Bash signal-pipe attempts failed under sandbox restrictions; the same bounded offline checks passed with normal local fixture access. Poppler emitted fallback-font notices for unused default font resources; used Vera body fonts are embedded, standard base-14 Courier code is searchable, and all reviewed glyphs display. pdffonts was unavailable; PDF font resources were inspected directly with pypdf. No unavailable tool or failed attempt was presented as a passing result.

### Command and configuration review

All 44 fenced reference blocks have risk/target context. Nine original core blocks remain exact; the existing Apache site retains every approved TLS/auth directive and adds explicit log paths; repository publication commands are replaced by links to the build/governance instructions. Existing member-health, Apache, Tailscale and interactive password behavior is preserved. Additions clarify the same required operations rather than adding systems/exercises.

Official references linked beside procedures were checked for Proxmox installer/bridges/permissions/firewall/storage, OPNsense installer/interface/rule/log behavior, Microsoft AD/DNS/domain/policy/events, Ubuntu/Netplan/nftables/systemd, OpenSSL 3.x, Apache 2.4 and Tailscale grants/CLI/device removal. The separate reviewer verified current OPNsense no-WAN assignment, Proxmox Datacenter input-policy location/mount guard, and nftables atomic replacement/overlay behavior against primary documentation/source. Proposed commands were reviewed and parsed where applicable, not executed on lab assets. Actual installed-version GUI paths, supported hardware, package behavior and recovery/remote results remain NOT TESTED.

## D. Security and Quality Review

The one-host/four-VM/three-zone model, ava/eli/uma, three role groups, separate privileged administrator, manual AD/app mapping, one CA/leaf, Tailscale-only remote path, five events, one investigation/operation/restore, six cases, ten FWR/FWT pairs, five deliverables and 25/25/20/20/10 rubric remain intact.

The guide retains exact disk/backup/recovery approval, original Windows preservation, lab-only identities/data, no production trust/sync, no protected-network probing, independent isolation before Internet, host/overlay enforcement and accurate negative-test controls. Restore uses an off-compute encrypted target, separate key custody, original-off/disconnected-copy state, inactive copied Tailscale, private integrity manifest and an existing bridge/client isolated for the drill. Temporary mocks/restore copy add no permanent VM/zone.

Manual review covers the complete candidate set, filenames, source/configuration examples, PDF text/metadata, report/history and later staged diff. No real address, credential, key, raw log, private inventory, backup or owner conversation is included. The original checkout's five archive deletions remain outside T8. Existing risks RK-01/02/06/07/16/18 and version/backup dependencies are explained without accepting them. Focused scans support, but do not replace, manual publication review.

## E. GitHub Operations

Authenticated identity: waqashamdani-ca, ID 315227303; push/admin permission verified. [Repository](https://github.com/waqashamdani-ca/enterprise-zero-trust-security): PUBLIC, default main. Both local author and committer identities resolve to 315227303+waqashamdani-ca@users.noreply.github.com. Global settings were not changed.

The clean isolated checkout started from main and git pull --ff-only origin main was already up to date. Read-only live inspection found no concurrent open PR, no active ruleset and main unprotected; no protection/reviewer setting was modified. The focused branch is codex/008-plain-english-lab-guide. Commit, push, PR, CI, merge and final synchronization remain pending at this draft cutoff; no future result or report-commit SHA is claimed.

## F. Outstanding Issues

No unresolved documentation defect after the final editorial read-back. Remaining implementation dependencies are owner approval of versions/backends/private values, delivered/compatible hardware and exact disk/recovery plan, lawful setup/activation, independently isolated egress and the selected encrypted-storage mount/unmount/recovery method. These are not completed by guide publication. No beginner usability trial or independent human review was performed. Publication/finalization remain to be observed.

## G. Completion Status

Local documentation verification: PASS. Separate AI editorial review and primary-agent PDF visual review: PASS. Report finalization/publication: IN PROGRESS. Independent human review: NOT TESTED. Owner UAT: PENDING. Lab implementation: PLANNED; operational controls/tests: NOT TESTED. No stage A-L or next task is authorized by these results.

## H. Next Task

Recommend exactly one bounded owner review of the rewritten guide and its remaining stage-entry choices. This review is not implementation approval. Any later stage A-L must receive its own explicit scope/assets/changes/validation/rollback approval before execution; no hardware readiness work begins in T8.
