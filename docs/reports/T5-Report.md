# T5 - Editable lab deliverable templates

Report state: FINALIZED

Evidence cutoff: 2026-11-06 08:43:23 UTC (2026-11-06 03:43:23, America/Toronto). Finalization date: 2026-11-06, America/Toronto. The report-finalization commit, its CI, merge and final main synchronization are outside this cutoff.

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T5 |
| Execution date | 2026-11-06, America/Toronto |
| Authorized scope | Create and validate the eight named editable Word/Excel shells in docs/deliverables/; update navigation and focused publication checks; report, publish by PR, verify CI, merge and synchronize main |
| Approval reference | Owner T5 Lab Deliverable Templates request, 2026-11-06; private original retained by owner |
| Dependency baseline | T4 report FINALIZED; PR 5 confirmed merged; local main, origin/main and live remote main all c5fa6ee4fa5eb3333b486d555fc71152ad0091c4 |
| Work preservation | Five report archive PDFs were already deleted in the owner's original working tree. An isolated clean worktree on task/005-lab-deliverable-templates preserves those uncommitted deletions and all frozen artifacts in T5 |
| Dependencies | Existing bundled artifact-tool, python-docx, native Microsoft Word/Excel and pinned documentation libraries; no software installation authorized or required |

The templates will help the owner record implementation accurately after separate stage approvals. Measurable outcomes are eight exact filenames, Segoe UI styling, editable fields, R01-R16 coverage, T00-T20 recording fields, blank actual/evidence fields, working spreadsheet controls and clean rendered layouts. Assignment, guide stage bodies, test definitions and rubric remain authoritative. Threat/control design and lab execution are outside T5; disclosure of private working records and confusing a template with executed evidence are the relevant risks.

Design: maintain inventory/capacity in 01, topology/flows in 02, identities/baselines/access policy in 03, stage configuration and recovery procedures in 04, monitoring measurements in 05, test verdicts/traceability/owner UAT in 06, defects/lessons in 07 and a referenced final assessment in 08. Keep actual readings blank. Cross-reference detail instead of collecting the same answer in different files. Reconcile workbook statuses with NOT TESTED and leave owner UAT PENDING.

Rollback: revert the reviewed T5 artifact/code/navigation changes in a new commit while preserving finalized reports and original owner work. Never rewrite history or remove historical records. No infrastructure recovery operation is needed.

## B. Implementation Summary

Created all eight files under [docs/deliverables](../README.md#editable-lab-deliverable-templates), with the exact assignment filenames:

| File | Structure and primary requirements |
| --- | --- |
| [01-Lab-Environment.xlsx](../deliverables/01-Lab-Environment.xlsx) | Five sheets: hardware, VMs, software, setup and resource allocation; R02 |
| [02-Architecture-and-Network-Design.docx](../deliverables/02-Architecture-and-Network-Design.docx) | Four pages: objectives, zones, diagrams, F01-F12 design, access, decisions, verification and limits; R01/R03/R04/R15 |
| [03-Identity-and-Access-Management.xlsx](../deliverables/03-Identity-and-Access-Management.xlsx) | Eight sheets: synthetic identities, groups, access matrix, authentication, privilege, endpoint baselines, revocation timing and verification; R05/R06/R08 |
| [04-Zero-Trust-Implementation.docx](../deliverables/04-Zero-Trust-Implementation.docx) | Five pages in Stage A-L order: configuration, PKI, separate remote pilots, automation, recovery and observations; R03/R04/R07/R09/R12/R13 |
| [05-Security-Monitoring.xlsx](../deliverables/05-Security-Monitoring.xlsx) | Eight sheets: six source classes, twenty events, detections, investigations, coverage, clocks, retention and observations; R10 |
| [06-Testing-and-Validation.xlsx](../deliverables/06-Testing-and-Validation.xlsx) | Eight sheets: test catalog, cases, requirements, recovery, evidence, engineering review, owner UAT and exceptions; R01/R13/R14 with complete R01-R16/T00-T20 recording coverage |
| [07-Troubleshooting-and-Lessons.xlsx](../deliverables/07-Troubleshooting-and-Lessons.xlsx) | One issue table: problem, impact, diagnosis, correction/rollback, verification, lessons and references; R14/R15 |
| [08-Final-Lab-Submission.docx](../deliverables/08-Final-Lab-Submission.docx) | Four-page blank assessment with supporting-file references, limitations, separate UAT, GitHub record and unchanged eleven-category 100-point rubric; R11/R15/R16 |

Word uses native heading styles, Letter pages, editable answer prompts/tables, diagram placeholders, headers and dynamic page numbers. Excel has 30 named tables across 30 sheets, filters, frozen headers/identifier columns, wrapped text and status dropdowns/conditional formatting. Segoe UI, restrained navy headers and pale input/calculation fills keep the set consistent. No protection, macros, embedded evidence, external workbook data connections or Office-template PDFs are included.

Only approved definitions and explicitly planned examples are seeded: ten VM allocations totaling 36 GiB RAM/248 GiB disk, six standard-user examples plus separate negative/privileged contexts, three role groups, twelve C01-C12 access expectations, twenty planned event IDs, and all 21 test definitions. The case register starts with 41 rows, including F01-F10 and C01-C12; its remaining placeholders must be expanded into all approved individual subcases before execution. Catalog headings are not the R14 denominator. Actual readings, observations, results, evidence, issues, dates and owner decisions remain blank or Pending. Unmeasured calculation outputs stay blank.

Updated README/library navigation, the current report index, DEC-22/CH-009, RK-20, build guidance and CI step labels. The lab guide receives one introductory link correction; no stage body changes. Added the standard-library [Office validator](../../scripts/validate_office_templates.py), its integration into the main validator and [twelve regression tests](../../tests/test_office_templates.py). Admission is limited to the exact eight XML-only packages, with bounded ZIP reads, relationship/field/formula inspection and normal public-content scanning. Unknown binaries remain rejected. Rebuilt the six affected documentation PDFs and the generated manifest; no report PDF or Office-template PDF was created.

## C. Testing and Validation

| Check | Expected / actual | Verdict |
| --- | --- | --- |
| T4 dependency | Finalized report and merged PR 5; exact local/remote main SHA equality observed | PASS |
| Existing work | Owner deletions preserved; separate clean T5 worktree created | PASS |
| python scripts/validate_office_templates.py | Eight exact files; expected sheets/tables, sections, R01-R16/T00-T20, C01-C12, twenty event fields, blank results/evidence, pending UAT and safe packages all verified | PASS |
| Native Microsoft Word 16.0 | All three final packages opened editable/unprotected; temporary text insertion and undo succeeded; 4/5/4 native pages rendered directly to PNG | PASS |
| Native Microsoft Excel 16.0 | All five packages and 30 sheets opened editable; named tables, filters, freeze panes and every Status dropdown/conditional rule checked; valid values accepted, invalid values detected, Pass/Fail colors changed | PASS |
| Formula change and boundary checks | Artifact-tool and native Excel independently recalculated allocation totals, timing, missing inputs, zero, reversed timestamps, 300/301-second latency, signed 2/2.001-second offsets and retention sizing; no formula errors | PASS |
| Native extension and owner fields | A new issue-table row inherited its dropdown; separate owner-decision dropdown worked; all QA edits closed without saving | PASS |
| Visual review | All 13 final Word pages, opening ranges of every worksheet and representative later-column ranges reviewed; readable headers, wrapped definitions, answer areas and no observed clipping/overlap | PASS |
| python -m unittest discover -s tests -v | All 50 focused tests passed, including twelve new Office safety/blank-field/definition-drift cases | PASS |
| python scripts/build_docs.py | Nineteen source/PDF pairs; six generated and thirteen unchanged; 98 pages in the maintained document set | PASS |
| python scripts/build_docs.py --check --rebuild-check | Nineteen pairs checked; fresh bytes match; no-change build generated zero and retained all nineteen | PASS |
| Documentation PDF review | Searchable text, source/hash/link/navigation checks passed; seven representative title, contents, table, code and introductory pages across six changed PDFs visually reviewed | PASS |
| python scripts/validate_docs.py and git diff --check | 79 candidate files/35 Markdown files; local links, report history, publication scan, traceability and whitespace checks passed | PASS |
| T4 preservation | All twelve baseline report/archive files other than the editable INDEX are byte-identical; assignment/architecture/security/testing/acceptance/final template and evidence unchanged; guide from Stage A onward identical | PASS |
| Operational lab tests | Outside T5 scope; no execution | NOT TESTED |

All checks above were performed on 2026-11-06 by the Codex engineering verifier. Scope is repository-only T00 and publication-only T17; no passing T01-T20 lab result is claimed. The required --require-finalized gate will run against these final report bytes before completion/merge; its post-cutoff result belongs in the final chat response.

The canonical render_docx.py attempt failed because LibreOffice is absent on this Windows host. Reviewed recovery used installed Word's [Page.EnhMetaFileBits](https://learn.microsoft.com/en-us/dotnet/api/microsoft.office.interop.word.page.enhmetafilebits?view=word-pia) to create PNGs directly, without a PDF intermediate or software installation. Native Excel opening used [Workbooks.Open](https://learn.microsoft.com/en-us/office/vba/api/excel.workbooks.open) with external-link updating disabled. Restricted-process COM/temporary-fixture access initially failed; reviewed local execution completed the same checks. QA helper numeric marshalling and Word pagination caches were corrected before final checks. Visual QA removed an inherited title border and shortened a cramped rubric heading. One synthetic split-token negative test initially failed; paragraph/cell-aware text-run scanning fixed it, and the complete suite then passed. No real credential finding occurred.

A restricted Git PDF text-conversion helper failed during a staged read. The complete new-history review used git diff --no-textconv with separately inspected PDF/Office payloads; the focused history scan passed and all fourteen committed binary payloads matched the reviewed files before push. No publication scanner was disabled or waived.

Raw scripts, logs and previews remain outside public Git. Reviewed artifact identities at this local evidence snapshot:

| File prefix | SHA-256 |
| --- | --- |
| 01 | afb0a0ecaec2c76b665d83382414074f79debd0bc6b8f4394c365fb89abe5656 |
| 02 | 81b41b07cc6f5cb36ca1b4303bb4a5ad6c6a0222b23980299ce52af83a926c66 |
| 03 | 2c0fc70f5776bd7b4559a095fb965cdd08ca43c217d2170ef01579cae250d251 |
| 04 | cf600aeb6903ca167f43f3a0d12a17d4cd73f1fd978c05b8287931bf793c5985 |
| 05 | c9a1839a440689ae0bfff6556136dbda7d1d4b9c25c632224eb5e3cf716f6248 |
| 06 | 2c1ad86eaba5e26bc3ed401e71797fab6e45e199bb5554fca860b66289734530 |
| 07 | 95e5e8ad44035b325cd13d5c4310fdf7573e7b8870d39b8fd2cbcc90b62c93a7 |
| 08 | 49087edf0b43626d41c563a651b3495ee67d600d75cb67be5664c8b34f8d9dba |

## D. Security and Quality Review

Manual review covered the proposed tracked paths, complete text/code changes and Office content/metadata/relationships. All eight Office archives contain XML only; unused starter thumbnails/custom XML were removed. No credentials, actual internal addresses, hardware observations, raw logs, tenant details or private evidence were introduced. The scanner checks raw XML plus text joined within paragraphs/cells and withholds suspected values in findings. It is bounded and cannot establish absence of every secret or classify all proprietary content; manual review remains necessary.

Separate observations were artifact-tool calculations versus native Excel recalculation, OOXML structure versus Word/worksheet renderings, and local Git/baseline bytes versus remote metadata. These are observations by the same verifier, not independent human sign-off. New commits/merges must use the verified GitHub noreply author and committer. Existing historical metadata risk RK-17 remains unchanged. Workflows retain read-only permissions, pinned official checkout, full history, no retained credentials and no lab access. Licensing and repository/reviewer settings were not changed.

## E. GitHub Operations

| Item | Observed state at evidence cutoff |
| --- | --- |
| Repository | [waqashamdani-ca/Enterprise-Zero-Trust-Security](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security), PUBLIC, default main; repository ID 1447671295 |
| Authenticated account / permission | waqashamdani-ca; push/admin verified by connected GitHub and CLI/API observations |
| Task branch | task/005-lab-deliverable-templates; no conflicting T5 work was found during preflight |
| Dependency baseline | c5fa6ee4fa5eb3333b486d555fc71152ad0091c4; T4 report finalized, PR 5 merged, local/remote main equal; clean isolated checkout and git pull --ff-only origin main confirmed already up to date |
| Implementation commit | [ebe45b996f829de4be77eaad0686a043a3602e0f](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/commit/ebe45b996f829de4be77eaad0686a043a3602e0f); both author/committer are verified GitHub noreply; 27 reviewed paths |
| Pull request | [PR 6](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/pull/6), OPEN, MERGEABLE / CLEAN, exact head ebe45b996f829de4be77eaad0686a043a3602e0f |
| Push CI | [Run 42189371245](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/actions/runs/42189371245), completed / success at the implementation head |
| PR CI | [Run 42189502099](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/actions/runs/42189502099), completed / success at the same head; every validation job step succeeded |
| Review/protection observations | No requested reviews, submitted reviews or review threads; live main protected=false and active branch rules empty; no repository settings changed |
| Branch synchronization | git ls-remote confirmed the T5 branch at ebe45b996f829de4be77eaad0686a043a3602e0f and main at c5fa6ee4fa5eb3333b486d555fc71152ad0091c4 |
| Final report publication / merge / main synchronization | Pending this finalized report's commit/push and exact-final-head checks; not claimed at cutoff |

The GitHub connector returned 403 for PR creation; the existing authenticated GitHub CLI created PR 6 from the reviewed body file, and connector/CLI read-backs confirmed it. The configured lowercase origin redirects to the same case-renamed repository verified in T4; T5 did not rename it or change origin. Raw evidence and authentication material were not published.

After final report publication, recheck the exact PR head, CI, reviews, requests, threads and branch rules before a normal local merge with verified noreply author/committer. Push without force, confirm GitHub records the PR as merged, then fast-forward local main and compare live remote IDs. Those later observed outcomes belong in the final chat response. Merge does not supply owner UAT.

## F. Outstanding Issues

Final report publication, final-head CI, merge and main synchronization remain outside this cutoff. No unresolved local template/check defect is known. The owner's original tree has five pre-existing archive-PDF deletions, preserved and excluded from T5. It cannot be described as clean while those owner changes remain; T5 uses its separate reviewed worktree. The eight templates need owner UAT. Filled private working copies will need separate review before publication and a deliberate change to the blank-shell validation contract. Existing asset/disk/backup, egress, software/evaluation, remote-provider and recovery decisions remain open. No stage approval follows from T5.

## G. Completion Status

| Dimension | State |
| --- | --- |
| Local template implementation | VALIDATED for the stated Office/documentation scope |
| Report / publication | FINALIZED at cutoff; implementation branch and initial CI verified; final report publication, final-head CI, merge and main synchronization pending |
| Second observations | PASS for the methods in C/D; same engineering verifier |
| Independent human review | NOT TESTED / not performed |
| Owner UAT | PENDING; no explicit acceptance reference |
| Lab stages A-L | PLANNED / NOT TESTED; no execution |

Local engineering verification is complete for the stated scope, and this report is finalized after reviewing the actual local and initial publication evidence. The required finalized validator and remaining publication outcomes will be reported after observation in the final chat response. No independent human sign-off, owner acceptance, operational result or T6 work is claimed.

## H. Next Task

Recommend T6 only: a read-only Stage A hardware and isolation readiness assessment. Before execution, the owner must approve the exact assets, scope, existing tools, permitted read-only observations, validation, private evidence handling and recovery/stop conditions. No reboot, firmware change, installation, networking change or Stage B disk operation is included. Do not begin T6 during T5.
