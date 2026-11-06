# T7 - Microsoft Office lab deliverable consolidation

Report state: DRAFT

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T7 |
| Execution date | 2026-11-06, America/Toronto |
| Evidence cutoff | Pending report finalization; this draft records observed local verification only |
| Finalization date | Pending; final report publication, final-head CI, merge and synchronization will be verified after its cutoff |
| Authority | Owner T7 Microsoft Office Lab Deliverable Consolidation request, 2026-11-06; original retained privately |
| Authorized scope | Five exact editable Office templates; retirement of verified blank T5 shells; necessary navigation, governance, validation/regression/CI and adjacent document PDF updates; Markdown-only report; reviewed GitHub publication and synchronization |
| Dependency | T6B FINALIZED; PR 9 merged; main workflow 42285308983 SUCCESS; local/tracking/live main d408c4571105bd42396dd5e71aae22f4f3d9290c |
| Branch and preservation | codex/007-office-deliverables; clean isolated worktree and git pull --ff-only origin main already up to date; original checkout's five archive-PDF deletions preserved |
| Tools | Existing bundled Python 3.12.14, python-docx and artifact-tool; existing pinned documentation libraries/Poppler; installed Microsoft Word and Excel 16.0; no software or fonts installed |

The owner needs practical answer sheets for the approved four-week lab. The design reduces eight legacy submissions to five, keeps each detailed answer in one owning record and separates plans, observed configuration, engineering test results and owner acceptance. All ten FWR requirements, ten FWT tests, their mandatory subchecks and the approved 100-point rubric remain covered. No lab execution or T8 work is authorized.

Before authoring, the assignment, guide, architecture, security requirements, Test Plan, acceptance criteria, rubric, decisions/risks, reports, Office validation and CI were reviewed. Threats considered were lost owner records, obsolete scope, unsupported success claims, unsafe packages/metadata, broken formulas/links and unreadable answer areas. The validation plan used baseline/content inspection, bounded OOXML checks, negative fixtures, native Office behavior and rendered visual review. Rollback is a reviewed revert of editable T7 artifacts; preserve finalized reports, history and owner work.

## B. Implementation Summary

Exactly five active files replace the eight verified blank shells:

| Deliverable | Record and ownership |
| --- | --- |
| [01-Lab-Environment-and-Architecture.xlsx](../deliverables/01-Lab-Environment-and-Architecture.xlsx) | Five sheets: Hardware & Readiness, Virtual Machines, Network Zones, Allowed Network Flows and Resource Allocation. FWR-01/02; procurement and installation fields are separate and empty. Four planned VMs/three zones/eight approved flows; observed inputs empty. |
| [02-Identity-and-Zero-Trust-Implementation.docx](../deliverables/02-Identity-and-Zero-Trust-Implementation.docx) | Four pages/nine sections/six editable tables: AD users/groups, endpoint controls, separate app roles, one CA/leaf, six access cases, scoped Tailscale and application/remote revocation. FWR-03 through FWR-06. |
| [03-Security-Monitoring-and-Testing.xlsx](../deliverables/03-Security-Monitoring-and-Testing.xlsx) | Eight sheets: five event categories, one denial investigation, Test Cases, Requirements Coverage, one Automation Verification, one Backup & Restore, Evidence Index and separate Owner Acceptance. Owns operational execution records for all ten requirements/tests. |
| [04-Troubleshooting-and-Lessons.xlsx](../deliverables/04-Troubleshooting-and-Lessons.xlsx) | One Issue Log: issue/date/component/check, problem/impact, cause, correction, verification/retest, status, lesson and evidence. Six empty initial rows; native table-row extension verified. |
| [05-Final-Project-Submission.docx](../deliverables/05-Final-Project-Submission.docx) | Three pages/ten sections/four editable tables: executive summary, architecture placeholder, implementation/testing summaries, findings, lessons, limits, evaluation and supporting links. Rubric 25/25/20/20/10 totals 100; scores/results empty. |

Segoe UI, navy/gray headings/tables, pale answer cells, wrapped text, fitted widths, frozen headers/identifiers and filters support filling the set. Word uses Title/Heading 1 styles, margins, editable tables, screenshot/diagram placeholders and PAGE/NUMPAGES fields. Excel uses practical dropdowns, input validation and conditional status colors; only eight capacity totals/input-guard formulas remain. No macros, protection, external workbook connections, embedded evidence or Office-template PDFs exist.

### Legacy disposition and reused structures

All eight original owner files matched HEAD and finalized T5 byte for byte. Every old workbook and Word document was inspected; blank result/evidence fields and Word placeholders were verified. No owner-entered answers or evidence were found. Normal Git deletions retire them from the active directory; their bytes remain reachable at [the original T5 snapshot](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/tree/6f5352bb6d5e2eca37ac2384703367543530b952/docs/deliverables).

| Retired T5 file(s) | Useful structure retained in the new set |
| --- | --- |
| 01 Lab Environment; 02 Architecture and Network Design | Planned/actual resource ledger, verification/evidence columns, topology/zone/flow prompts and diagram references in 01 and 05 |
| 03 Identity and Access Management; 04 Zero Trust Implementation | Role/configuration summaries, endpoint and trust prompts, explicit revocation/case references and expected/actual separation in 02/03 |
| 05 Security Monitoring; 06 Testing and Validation | Event/context records, exact test definitions, individual cases, coverage/evidence index and separate owner decision in 03 |
| 07 Troubleshooting and Lessons; 08 Final Lab Submission | One practical issue table, summarized findings/limits, supporting references and rubric in 04/05 |

The new set removes the old six-zone/six-user/dual-provider/two-tier-CA/twenty-event/twelve-case/two-operation and enterprise-recovery targets. R01-R16/T00-T20 are absent from active templates; historical mappings and finalized evidence are preserved. No historical PASS was reused.

### Traceability and other changed paths

The ten OVERALL rows in Test Cases quote the current plan's objective/method, scope, expected outcome and second observation exactly. Ninety-one numbered child recording rows divide those existing methods into observable checks; they are not extra test IDs or new scope. They expose C01-C06, app existing/fresh revocation, remote permit/identity/port/existing/new revocation, trust/validity, five event categories, one automation with safe repetition/rejection and one isolated APP1 restore. Detailed configuration/automation/recovery records are referenced rather than copied. All actuals, execution dates, evidence, defects and retests start empty; statuses NOT TESTED. NOT APPLICABLE cannot waive a mandatory check. Owner decisions start PENDING on their separate sheet.

| Other changed paths | Purpose |
| --- | --- |
| [README](../../README.md), [documentation library](../README.md) and their PDFs | Five active downloads, current ownership/availability and original T5 snapshot navigation |
| Assignment/guide sources and PDFs; Test Plan/acceptance sources and PDFs | Release/navigation sentences only; no changed requirement, outcome, control, approval or command block |
| [DECISIONS](../governance/DECISIONS.md)/PDF, [RISKS](../governance/RISKS.md)/PDF | DEC-27/CH-011 record the authorized migration; RK-20 records disposition and residual conditions |
| [Build guide](../governance/DOCUMENTATION-BUILD.md)/PDF and generated manifest | Current bounded five-file validation, source/PDF hashes and preservation rules |
| [Office contract](../../scripts/office_template_contract.py), [Office validator](../../scripts/validate_office_templates.py), [documentation validator](../../scripts/validate_docs.py) | Exact files/sheets, current plan/subchecks/flows/cases/rubric, blank fields, fonts, safe packages/formulas and frozen-report snapshot links |
| [Office tests](../../tests/test_office_templates.py), [documentation tests](../../tests/test_validate_docs.py), [PDF tests](../../tests/test_build_docs.py), [CI](../../.github/workflows/documentation.yml) | Negative fixtures and migration/preservation regressions; explicit read-only Office validation step |
| [Report index](INDEX.md), this report | T7 navigation and accurate Markdown-only evidence record |

The complete footprint is 41 paths: 26 changed baseline files, eight retired files and seven additions (five Office files, contract and report). Forty-eight of the 82 baseline files remain byte-identical, including all 16 historical report/index/archive files except the separately editable current INDEX, public evidence, architecture/security specifications, AGENTS and the visibly uncompleted project final-report template. Fifteen unrelated/archived PDFs retain their bytes. No infrastructure/configuration source or repository setting changed.

## C. Testing and Validation

Execution date for these observations: 2026-11-06. Verifier: Codex. Separate source/Git/package/render/native observations below are engineering verification by the same verifier, not independent human review. Private audit records, native JSON, test output and previews remain outside the public tracked set.

| Executed check / expected outcome | Actual observation | Verdict |
| --- | --- | --- |
| T6B/Git/owner-file preflight | Finalized T6B, merged PR 9, successful exact-main CI and matching local/live baseline; authenticated owner/push/admin; original five deletions and all eight unmodified owner shells verified | PASS |
| Legacy content/package and hash audit | Eight T5 originals match owner/HEAD/published T5; 30 old sheets and three Word shells inspected; no entered answers/evidence | PASS |
| python scripts/validate_office_templates.py | Exactly five XML-only packages/14 sheets; exact ten-test definitions and 91 child records, FWR/FSC/FWT/FAC mappings, eight flows, six Word cases, fonts, controls, blank fields and 100-point rubric | PASS |
| Artifact-tool recalculation and error inspection | Planned vCPU/RAM/disk 8/20/176; storage ledger 336 GiB; changed actual inputs recalculate; partial inputs remain blank; zero distinct from missing; temporary values restored; zero formula-error matches | PASS |
| Native Microsoft Word 16.0 inspection | Both documents open editable/unprotected; temporary insert/undo works; visible text uses Segoe UI; Title/Heading 1/table structures and two footer fields verified; final pagination 4/3 pages | PASS |
| Native Microsoft Excel 16.0 inspection | All three books/14 sheets open editable; named tables, actual filters, row-7/column-2 freeze panes, Segoe UI and status validation checked; listed value valid, invalid value detected, PASS/FAIL colors change | PASS |
| Native Excel recalculation and extension | Independent engine confirms 8/20/176/336 planned and changed actual totals; missing/zero guards; added issue row inherits dropdown; all QA edits closed without saving | PASS |
| Every-page Word and all-sheet visual review | Seven final native Word page images, all 14 sheet opening ranges and four later-column ranges inspected; readable answer areas, tables/headers, true page totals and no clipping/overlap/blank page observed | PASS |
| python scripts/build_docs.py | Nine changed document PDFs rebuilt; 19 maintained pairs/81 pages. Office files and entire report directory receive no generated PDFs | PASS |
| python scripts/build_docs.py --check --rebuild-check | Every source/PDF/hash/text/link/navigation record matches fresh deterministic rendering | PASS |
| No-change build plus independent SHA-256/mtime snapshot | Generated 0, unchanged 19; all 24 maintained/archive PDF hashes and mtimes stable | PASS |
| Poppler representative visual review | 26 distinct title/table/contents/code/page-transition pages across all nine changed PDFs reviewed; library label and DEC-27 table presentation corrected and reinspected | PASS |
| python scripts/validate_docs.py | 81 candidate files/39 Markdown sources; current links, verified original T5 snapshot targets, mappings, workflow, report numbering/history and eleven frozen migration hashes pass | PASS |
| python -m unittest discover -s tests -v | 77 tests PASS at final local source/PDF tree; unsafe packages/formulas/relationships, hidden split token, outcome/actual/score drift, lost child check, source-plan/flow/case drift, font/compatibility prefix, UAT and frozen history negatives included | PASS |
| git diff --check and git diff --cached --check | No whitespace finding; complete proposed paths, source/code changes and binary package/PDF contents reviewed manually | PASS |
| Independent baseline and current-plan comparison | 48 unchanged baseline paths, 16 historical report files, 15 unchanged PDFs; all ten methods/scopes/outcomes/second observations and eleven guide code blocks unchanged; original owner shells still match | PASS |
| Lab FWT-01 through FWT-10 execution | No infrastructure, remote enrollment, automation operation, backup/restore or security test executed | NOT TESTED |
| Independent human review / owner UAT | No second human reviewer or explicit owner confirmation | NOT TESTED / PENDING |

The canonical render_docx.py attempt failed because LibreOffice is absent. Installed Word's [Page.EnhMetaFileBits](https://learn.microsoft.com/en-us/dotnet/api/microsoft.office.interop.word.page.enhmetafilebits?view=word-pia) supplied direct private PNG rendering with no PDF intermediate. Native opening used the [Excel Workbooks.Open](https://learn.microsoft.com/en-us/office/vba/api/excel.workbooks.open) object model with link updates disabled; [CalculateFullRebuild](https://learn.microsoft.com/en-us/office/vba/api/excel.application.calculatefullrebuild) and [Validation.Value](https://learn.microsoft.com/en-us/office/vba/api/excel.validation.value) supplied behavioral checks.

During QA, font/default inheritance, an intermediate XML prefix error, lazy page totals and preview DPI were corrected before final native checks. The optional Computer Use app-launch approval timed out; no GUI-click-through result is claimed. Native document-model checks and direct render review completed. Restricted-process temporary fixtures initially failed access checks; the same bounded tests passed under reviewed local execution. Three old test-fixture coordinates and two T6-only preservation assertions were migrated to the authorized T7 contract, then all 77 tests passed. No unresolved finding or scanner bypass remains. Poppler emitted base-font fallback notices; inspected pages retained readable text/code and no missing glyph was observed.

Office SHA-256 values at the local evidence snapshot:

| File | SHA-256 |
| --- | --- |
| `01-Lab-Environment-and-Architecture.xlsx` | `33a0a1ac1204c308b89cff131463d7c75f7ef804aeeef4d61073993f790b26c0` |
| `02-Identity-and-Zero-Trust-Implementation.docx` | `5ff8ce00c7d83d530643cdbb8c32c6f1ccb8b9e9f9fd26f7dbc80c60824d4d54` |
| `03-Security-Monitoring-and-Testing.xlsx` | `1281d20065d0c74e06e8e2490c81b99086f030b94af57fa75e465cda10e866ec` |
| `04-Troubleshooting-and-Lessons.xlsx` | `084423d2c1daa47a23a8fe9bc2afb0cbc02866e6d0fca836050ead604fd368ae` |
| `05-Final-Project-Submission.docx` | `6e5622322ab962e03b159e31d4d5b1098d89de656fb7151ac09c24b7f53100c6` |

## D. Security and Quality Review

Only reviewed public-safe templates, text/code and known generated PDFs are proposed. No credentials, actual addresses, private inventory, corporate records, raw logs/evidence, recovery data or fabricated screenshots/results appear in the five templates. Every Office member is XML; package bounds, relationships, field/formula admission, protection/active content and markup compatibility are checked. These bounded checks do not prove absence of every possible sensitive detail; manual content/metadata/history review remains required at publication.

All finalized reports and archived PDFs remain byte-frozen. The unmodified T5 report's eight retired relative targets are checked against its exact published snapshot only; changed/current source cannot use this exception. Library/report-index links open that original revision so historical navigation works. Missing history or changed frozen text fails closed. No history rewrite occurred.

The original checkout retains five owner archive-PDF deletions; T7 neither commits nor recreates them. The clean engineering worktree and committed history retain all archives. Production/home boundaries, synthetic identities/data, separate remote lab environment, explicit stage approvals and no protected-network probes remain in force. Licensing, rulesets/review settings, existing historical identity metadata risk RK-17 and all infrastructure decisions remain owner matters.

## E. GitHub Operations

| Item | Observed state at this draft |
| --- | --- |
| Repository | [waqashamdani-ca/Enterprise-Zero-Trust-Security](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security); PUBLIC, default main; repository ID 1447671295 |
| Identity and permission | waqashamdani-ca; push/admin confirmed through connected repository metadata and CLI/API read-back |
| Author and committer | Both Git identities verified as the owner's GitHub noreply identity; recheck each new commit and merge before push |
| Base / live main | d408c4571105bd42396dd5e71aae22f4f3d9290c, exact T6B merged baseline |
| Task branch | codex/007-office-deliverables, clean isolated baseline with --ff-only pull |
| Publication commit / PR / CI | Pending; no future result or self commit SHA claimed |
| Merge rules | main protected=false; live branch rules empty; merge-commit method allowed; no settings changed. Recheck exact head, reviews/requests/threads/checks before merge |
| Merge / main synchronization | Pending final report publication and applicable completed-head checks |

The completed report will name an evidence cutoff. Its own commit, later CI, merge and synchronization cannot be recorded prospectively. Observe those after publication and report them in the final response; later written corrections require a separate addendum. A normal permitted local merge may preserve verified noreply identities only after exact-head checks and applicable reviews/rules pass. No force push or approval bypass is authorized.

## F. Outstanding Issues

- Final report finalization/publication, completed-head CI, merge and synchronization are IN PROGRESS at this draft; no local Office/documentation defect remains.
- Original working folder still has its same five archive-PDF deletions. Its documentation check will report missing archives until the owner reconciles those pre-existing changes; clean engineering-worktree checks pass.
- Lab readiness/delivery/compatibility, selected versions/backend, exact disk/data-service backup/recovery approval and independent safe egress remain unverified dependencies. No template availability or repository check resolves them.
- Independent human review is NOT TESTED and owner UAT remains PENDING. Repository protection/reviewer choices and licensing remain explicit owner decisions; historical metadata is preserved.

## G. Completion Status

| Area | State |
| --- | --- |
| Five-template implementation | IMPLEMENTED; local Office/content/formatting checks VALIDATED |
| Local engineering verification | PASS for the bounded template/documentation scope; 77 regressions and separate native/package/render observations |
| Report / publication | DRAFT / IN PROGRESS; finalization, final-head publication checks, merge and main synchronization pending |
| Independent human review | NOT TESTED |
| Owner UAT | PENDING; no confirmation reference exists |
| Operational implementation / lab controls | PLANNED / NOT TESTED; no infrastructure change or operational FWT PASS claimed |

This draft does not declare T7 engineering completion. Stop after final verification/reporting and intentional GitHub synchronization. No T8 or implementation stage is started.

## H. Next Task

Recommend T8 only: a read-only Stage A hardware and isolation readiness assessment. Before execution, obtain explicit owner approval naming exact assets, read-only scope, existing tools, permitted observations, validation, private evidence handling and stop/recovery conditions. No reboot, firmware change, installation, disk selection/formatting, VM/network change or later stage is included. Await owner review; do not begin during T7.
