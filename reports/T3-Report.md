# T3 report — PDF documentation and folder organization

Report state: DRAFT

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T3 |
| Title | PDF documentation and folder organization |
| Execution date | 2026-11-05, America/Toronto |
| Scope and objectives | Organize editable documents by purpose, generate faithful professional PDFs, implement a reproducible Windows build and CI checks, preserve historical sources, and publish through the normal PR workflow |
| Dependencies | Owner PDF/folder addendum; completed T2/reporting governance; inspected free PDF toolchain; authenticated repository access; no infrastructure approval |
| Branch / baseline | `task/003-pdf-documentation`; `ab0a96e3c4dc6cb113818ee3b57ee4618a0d8cc8` |

## B. Implementation Summary

Moved eleven editable sources into purpose folders: assignment to `docs/assignments/`, lab guide to `docs/lab-guides/`, architecture to `docs/architecture/`, security to `docs/security/`, test plan/acceptance to `docs/testing/`, decisions/risks/references to `docs/governance/`, the final template to `docs/final-report/`, and glossary to `docs/guides/`. Updated current navigation, README, AGENTS.md, the report index, validator paths, and CI. Two small decision/risk compatibility pages preserve links in immutable reports; they are not duplicate source editions.

Preserved finalized T1, its addendum, T2, and bootstrap evidence byte-for-byte. Generated twenty-four adjacent PDFs: thirteen documentation/library/build editions, five report/index editions, two root guides, and four folder/evidence editions. The [documentation library](../docs/README.md) and [generated manifest](../docs/documentation-manifest.json) identify each source/PDF pair. The project final report remains visibly a template, with no invented implementation results.

Used inspected bundled Python 3.12.14, ReportLab 4.4.9, pypdf 6.10.0, and Poppler 26.07.0. Added only Mistune 3.4.0/Pygments 2.21.0 to an ignored project-local dependency folder; pinned the full documentation dependency set for Windows/Linux. Added `scripts/build_docs.py`, `tests/test_build_docs.py`, `requirements-docs.txt`, the generated manifest, library/build instructions, generated PDFs, and this report. Updated `.gitattributes` for stable text/binary handling and `.gitignore` for temporary previews/local environments. CI installs only documentation dependencies and checks fresh regeneration.

The deterministic renderer embeds fonts, adds source-derived document versions, numbered headings, title/contents pages where appropriate, repeatable table headers, highlighted/wrapped code, vector architecture, page numbers, clickable references, and named heading destinations. All twelve planned stages gained explicit Objective, Required tools, and Troubleshooting fields alongside their existing procedures/checks/rollback. No procedure was executed. No infrastructure, production, account privacy, project license, or global software setting changed.

## C. Testing and Validation

| Check | Expected result | Observed result | Status |
| --- | --- | --- | --- |
| Source migration and internal links | Content/IDs/commands preserved; all current and historical navigation resolves | Eleven moves accounted for; all links passed; sixteen requirements and the rubric/control/architecture tables retained; eight original lab code blocks unchanged; twelve stages have all ten required fields | PASS |
| Frozen report/evidence comparisons | All finalized historical bytes unchanged | Exact Git-baseline comparisons passed for all four finalized/historical Markdown artifacts | PASS |
| PDF batch build | Every approved source has an adjacent readable/searchable PDF | Twenty-four source/PDF pairs generated and opened; every PDF has extractable/searchable text | PASS |
| PDF source/structure/navigation check | Correct source hashes, pages, text coverage, links, bookmarks, and footers | Implementation snapshot: 123 pages, 100% normalized source-token coverage, 191 per-document URI links, 309 named heading destinations, valid footers and no orphan headings | PASS |
| Deterministic rebuild | Fresh render matches existing output and no-change build causes no churn | Full fresh in-memory rebuild matched bytes; no-change build skipped all twenty-four outputs; an isolated table-column improvement changed only its two affected PDFs | PASS |
| Representative visual inspection | Readable title/TOC/tables/code/diagram/page breaks; no clipping/overlap/missing glyphs | Viewed all twenty-four first pages and eleven detailed samples; corrected empty-page/orphan/narrow-column issues; final character-bound checks found zero violations across the snapshot | PASS |
| Focused tests and publication checks | Actual test results recorded; new public artifacts clean | All twenty-five tests passed; generated PDF text/metadata and source scans had zero selected new-artifact findings; unknown/drifted PDFs rejected | PASS |
| GitHub PR/CI/merge and synchronization | Exact-head checks/requirements pass; normal noreply merge; matching main refs | Pending | NOT TESTED |

## D. Security and Quality Review

PDFs must be generated from reviewed public-safe Markdown without raw evidence, actual addresses, secrets, private filesystem paths, or executable content. New binary publication is restricted to source-matched manifest-listed PDFs. The project final report remains a template with no fabricated implementation or acceptance.

Executed `scripts/build_docs.py`, `scripts/build_docs.py --check --rebuild-check`, `scripts/validate_docs.py`, `python -m unittest discover -s tests -v` with the documented dependency runtime, Git whitespace/source-history checks, Poppler page rendering, and independent pypdf/pdfplumber text/metadata/geometry inspection. Initial text/layout guards exposed split decision IDs and table pagination issues; ID widths, long-table grouping, and heading placement were corrected, then PDFs were rebuilt and inspected again. These were documentation defects, not lab/security findings. Code/diagram source and requirement/control tables were compared with the Git baseline rather than inferred from a build success flag.

Historical email metadata RK-17 remains an owner decision; no history rewrite is authorized. All operational lab/security/isolation tests remain NOT TESTED. Visual checks and text extraction are separate observations; neither implies owner UAT.

## E. GitHub Operations

| Item | Observed state at draft creation |
| --- | --- |
| Repository / branch | `waqashamdani-ca/enterprise-zero-trust-security`; `task/003-pdf-documentation` |
| Dependency PR | [PR 2](https://github.com/waqashamdani-ca/enterprise-zero-trust-security/pull/2) merged at `ab0a96e3c4dc6cb113818ee3b57ee4618a0d8cc8`; both merge identity fields were noreply; local/remote main matched |
| Dependency merge CI | [Run 42144602697](https://github.com/waqashamdani-ca/enterprise-zero-trust-security/actions/runs/42144602697): success |
| T3 commit / PR / CI / merge | Not yet published |
| Synchronization | Started from verified clean main; final read-back pending |

## F. Outstanding Issues

Local build, artifact checks, tests, and visual review are complete; branch/PR CI and final publication read-back remain pending. The renderer supports the repository's reviewed Mermaid flowchart subset and fails on unsupported syntax; it is not a general Mermaid engine. External/named-destination behavior depends on the PDF reader. Typography normalizes unsupported arrow/dash glyphs without modifying Markdown. Visual samples and automated geometry checks are separate from owner acceptance.

Historical email metadata RK-17, prior external-reference transport limits, owner UAT, and future hardware/egress/backup/license/protection decisions remain unresolved. No new reachability or operational security claim is made. The final report's own PDF/hash/page count will be rebuilt and checked again after finalization; final publication results belong to the PR/final response after the stated evidence cutoff.

## G. Completion Status

| Area | Status |
| --- | --- |
| Engineering | IN PROGRESS |
| Independent verification | Pending source comparisons, PDF extraction/render review, fresh rebuild, and hosted CI; no independent human review claimed |
| Owner UAT | PENDING |
| Remaining owner decisions | Acceptance of documentation/PDFs; historical email privacy remediation; separate approval for any future lab work |

## H. Next Task

Stop after this documentation/PDF scope and request owner review. The next recommended bounded engineering task remains a read-only Stage A hardware and isolation readiness assessment. It requires separate explicit owner approval, confirmed asset access/ownership, and private evidence handling. No Proxmox installation, network configuration, VM creation, or infrastructure/security testing is authorized here.
