# T6A - Project Assignment editorial, design and layout improvement

Report state: DRAFT

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T6A |
| Execution date | 2026-11-06, America/Toronto |
| Authority | Owner T6A Project Assignment Content, Language, Design and Layout Improvement request, 2026-11-06; private original retained by owner |
| Scope | Assignment editorial/design/layout improvement and necessary renderer, validation, manifest, build-reference and reporting navigation changes; reviewed GitHub publication/CI/merge/synchronization |
| Dependency baseline | T6 FINALIZED; PR 7 merged; local main, origin/main and live remote main 36a2eb0a5e65dd344b165dda158d75b129f5585b; final-head PR workflow 42205248861 successful |
| Branch / preservation | codex/006a-assignment-quality in an isolated clean worktree pulled from main with --ff-only; five pre-existing owner archive-PDF deletions remain untouched in the original checkout |
| Reporting exception | Owner expressly requested T6A-Report.md. It is a companion to finalized T6, with A-H/state/history protection; it allocates no T7 number and authorizes no other lettered task |
| Dependencies | Existing bundled Python/pinned ReportLab/Mistune/Pygments/pypdf and Poppler. No software or font installed |

The reader outcome is a concise, practical assignment that explains the business scenario, required work, submission and assessment without internal task terminology. Measurable targets: three or four pages; intact exact filenames; correct separate Windows/application identity model; concise readiness without unconfirmed procurement claims; ten unchanged requirement/test mappings and rubric weights; searchable/linkable PDFs; supporting-specification/Office/history preservation.

The editorial design replaces nine sections/large contents area with eight numbered sections, bullets and short tables. Relevant risks are semantic scope drift, misleading availability/readiness/SSO claims, broken legacy links, layout defects, nonportable fonts and disclosure through publication. This is documentation-first work with no lab-control implementation. Rollback is a normal reviewed revert of editable T6A artifacts/code, preserving finalized reports and owner changes.

## B. Implementation Summary

| Changed file | Improvement |
| --- | --- |
| [PROJECT-ASSIGNMENT.md](../assignments/PROJECT-ASSIGNMENT.md) and adjacent PDF | Eight sections, natural direct language, short objectives/components/exclusions, concise requirements and one checkpoint for each of five phases |
| [build_docs.py](../../scripts/build_docs.py) | Assignment-only title/header/typography, no contents list, light tables, intact filenames, aligned points, retained bookmarks and compatibility anchors; short tables/lists kept together |
| [validate_docs.py](../../scripts/validate_docs.py) | New headings/two-column table contract, identity/readiness/availability/jargon checks, safe legacy-anchor navigation and explicit protected T6A companion naming |
| [test_build_docs.py](../../tests/test_build_docs.py), [test_validate_docs.py](../../tests/test_validate_docs.py) | Real-PDF filename/page/bookmark checks, malicious-HTML rejection, source/PDF preservation and companion-parent/immutability negative cases |
| Generated manifest | Builder-produced hashes/navigation/renderer fingerprint; no hand-edited hash suppression |
| [DOCUMENTATION-BUILD.md](../governance/DOCUMENTATION-BUILD.md) and PDF | One paragraph updated to describe the current assignment layout/compatibility navigation accurately; no other build-guide content changed |
| [Report index](INDEX.md), this report | T6A link and explicit owner-authorized companion convention; Markdown only |

Eleven scoped paths including this report; ten existing tracked files change. Architecture, Lab Guide, security requirements, test definitions, acceptance criteria, decisions/risks, AGENTS.md, README/library, Office templates and finalized historical records remain byte-identical.

| Measure | Before | After |
| --- | --- | --- |
| Assignment PDF pages | 4 | 4 |
| Assignment source words | 1,255 | 1,180 |
| Numbered main sections | 9 | 8 |
| Deliverable-table columns | 3 | 2 |
| Exact filenames shown whole | Second filename split across lines | All five exact names on single lines, together on one page |
| Contents list | Large first-page contents area | Removed; eight numbered headings and PDF bookmarks retained |

Word count is len(source.split()) on UTF-8 Markdown, including headings/table/link/anchor tokens; the same method is used before/after. The source is 75 words shorter, approximately 6.0%; this is not a measured readability grade. No filler or extra cover page was added.

Language changes include a short fictional business scenario, outcome-oriented bullets, explanations of VM/AD/DNS/CA/HTTPS where useful, less shorthand and fewer repeated status/governance statements. The assignment contains no T6/T7/T6A or A-L task/stage labels; FWR/FWT labels are explained once and retained.

Identity clarification says AD manages Windows accounts; the application has separate test accounts, distinct passwords and manually assigned roles. Removing an app role must deny further access; enterprise single sign-on is excluded. No AD integration/SSO work was added.

Hardware models/delivery dates were removed from the assignment. Existing/ordered hardware readiness, original disk/data/service preservation, backup/recovery and owner approval before destructive/high-risk changes remain. All procurement detail already exists in the authoritative Lab Guide, so nothing was duplicated or moved and the guide was not edited. Ordered is not presented as delivered, installed or validated.

The four-week target, one Proxmox host/four VMs/three zones, three standard users/groups/one privileged administrator, six app cases, Tailscale-only named-resource access, one CA/leaf, two or three sources/five events/one investigation, one operation and one backup/restore are unchanged. FWR-01 through FWR-10 retain FWT-01 through FWT-10. All mandatory subchecks/critical safety gates and separate owner UAT remain required. Rubric categories/weights remain 25/25/20/20/10, total 100, with no implementation credit for plans.

Six invisible legacy section IDs preserve existing Markdown and PDF links without editing/rebuilding the Lab Guide or other core specifications. They point to the correct renamed headings, not extra visible sections. No manual breaks, abbreviations or filename changes were introduced. The filename column uses a measured-width check and fails if a name cannot fit intact.

Font choice: Segoe UI is installed locally, but the existing pinned Ubuntu CI toolchain does not include it or an approved distributable font asset. The assignment retains embedded package Vera for reproducible local/CI rendering. No font binary, new license selection or machine-specific font path is published. Ten-point body/nine-point table text, restrained navy/charcoal/gray, subtle separators, consistent indentation and simple page furniture provide the academic/business layout.

## C. Testing and Validation

Engineering verifier: Codex. Separate tool/source observations below were performed by the same verifier; no independent human sign-off is claimed. Raw previews/logs stay in ignored private working locations; reviewed public sources, PDFs, tests and eventual CI provide reproducible evidence.

| Executed check / expected result | Actual observation | Verdict |
| --- | --- | --- |
| Git/T6/publication preflight | PR 7 merged, T6 report FINALIZED, final-head CI SUCCESS, exact local/live main baseline; authenticated owner and noreply identities verified | PASS |
| Baseline Markdown/PDF review and Poppler render | Four pages/1,255 words; old second filename split, large contents list and hardware/task detail observed | PASS |
| Semantic comparison against T6 assignment/supporting specifications | All scope/counts, ten same-numbered FWR/FWT mappings, five filenames, rubric weights, safety and UAT meaning preserved; separate-app explanation made explicit | PASS |
| python scripts/build_docs.py | All 19 maintained pairs/78 total pages generated/checked; exactly assignment and one-paragraph build-guide PDF bytes changed | PASS |
| python scripts/build_docs.py --check --rebuild-check | Fresh rendering bytes match; source/hash, text, page, link, metadata and bookmark checks pass | PASS |
| No-change build plus separate hash/mtime snapshot | All 24 maintained/archive PDF hashes and modification times unchanged; builder reports 19 unchanged pairs | PASS |
| python scripts/validate_docs.py | 81 candidates/37 Markdown files; structure, mappings, links/anchors, reporting/history, workflow and focused publication checks pass | PASS |
| python scripts/validate_office_templates.py | Eight legacy Office packages, 30 worksheets and pinned old blank-shell definitions remain intact | PASS |
| python -m unittest discover -s tests -v | 65 focused tests PASS, including HTML rejection, full-line filenames, original artifact preservation, T6A parent/state/immutability and rejection of unapproved lettered report names | PASS |
| Independent baseline SHA-256 and direct committed-byte comparisons | 70 of 80 baseline files unchanged; all eight Office templates, all core specifications, evidence and finalized reports preserved; 22 unrelated/archived PDFs unchanged | PASS |
| PDF text/legacy destination inspection | All five exact filenames together on one page; all ten FWT labels together in requirements table; all six legacy destinations resolve to their correct new heading pages | PASS |
| Every-page visual review | All four final assignment pages and all three build-guide pages inspected; no clipping/overlap/orphan headings/awkward filename breaks observed; complete short tables, readable bullets/headers/footers | PASS |
| git diff --check and manual source/code/candidate review | Whitespace clean, only the scoped files differ, synthetic/public-safe content and no operational result fabrication | PASS |
| --require-finalized completion gate | To run after report finalization and before merge; not yet executed for the finalized T6A state at this draft cutoff | NOT TESTED |
| Lab/security tests, readiness, installation and owner UAT | No infrastructure operation, lab test, procurement or Office edit performed; no owner acceptance confirmation | NOT TESTED |

Initial layout trials were corrected before review: a forced section break created an extra page; table/bullet grouping and spacing restored four useful pages. Narrow Week/Points headers were widened; requirement, filename, schedule and rubric tables now stay intact. Initial HTML parsing rejected bare compatibility anchors; the renderer now admits only identifier-only assignment anchors and still rejects active attributes. Historical T1 Task ID parenthetical forms were preserved in the companion-report validator; no frozen report was edited.

Poppler reported Symbol/ArialUnicode display-font warnings during rendering; all reviewed text/glyphs were legible using embedded document fonts. Extraction confirmed content/navigation, while rendered pages supplied the layout observation. Automated checks do not establish owner usability acceptance or lab security.

## D. Security and Quality Review

No lab implementation command, infrastructure configuration, lab connectivity change or lab test was performed. No new lab system, lab technology, operational test or submission deliverable was introduced. No Office file was opened for editing or regenerated. Existing lab designs, acceptance/test definitions and all finalized records remain unchanged.

The full proposed public set, filenames, edited text/code, generated PDF metadata/content and current diff were manually reviewed alongside bounded scanners. No secret, actual address, private inventory, procurement identifier, raw evidence, proprietary source or unreviewed binary was introduced. No scanner/protection was bypassed, and no license, account privacy, workflow privilege or repository reviewer/ruleset setting changed.

The one supporting build-reference paragraph/PDF is necessary to avoid stale contents/layout instructions. All other PDF bytes are preserved. The general report numbering/state/history rules remain; only explicitly authorized T6A is admitted as a finalized-T6 companion, with no automatic T7 allocation or permission for other lettered reports.

## E. GitHub Operations

Authorized repository is public, default main, using existing origin; verified owner login waqashamdani-ca has push/admin permissions. Both new author/committer identities are the existing GitHub noreply identity; global settings were not changed.

Branch: codex/006a-assignment-quality. Baseline main: 36a2eb0a5e65dd344b165dda158d75b129f5585b. At this draft cutoff no T6A commit, push, PR, CI, merge or final synchronization is claimed. Finalization will record only observed publication evidence; later completed-head CI/merge/main state will be reported in the final chat response.

## F. Outstanding Issues

No known unresolved local editorial/layout/check failure. Templates remain planned/unavailable pending separately authorized T7. Hardware delivery/readiness, safe isolated egress and each implementation-stage approval remain future dependencies. Font portability is preserved through the existing embedded font; a different font would need an approved portable build strategy.

Owner UAT PENDING; independent human review NOT TESTED. Original checkout retains its five owner PDF deletions and is not clean; T6A engineering uses the isolated checkout. Initial publication, report finalization gate and final GitHub/CI/merge/synchronization remain pending at this draft cutoff.

## G. Completion Status

| Area | State |
| --- | --- |
| Assignment editorial/layout implementation | IMPLEMENTED / locally VALIDATED for checks above |
| Second observations | PASS through rendered pages, PDF/Markdown/navigation comparison and byte-preservation checks; same engineering verifier |
| Independent human review | NOT TESTED |
| Report / GitHub publication | DRAFT / pending |
| Operational lab implementation | PLANNED / NOT TESTED; no operation performed |
| Owner UAT / acceptance | PENDING |

## H. Next Task

Recommend **T7 only**: migrate the eight legacy Office shells into the five approved templates after explicit owner approval of exact scope, filenames, preservation/replacement, requirement/test/rubric mappings, native/visual/formula validation and rollback. Do not begin T7 or lab implementation in T6A. Stop after publication/synchronization and await owner review.
