# T3 addendum 001 — Markdown-only task reporting

Report state: DRAFT

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T3 |
| Title | Governance addendum: Markdown-only task reporting |
| Execution date | 2026-11-06, America/Toronto |
| Scope and objectives | Exclude all of reports/ from PDF generation; retain Markdown reporting and immutable historical records; preserve user-facing document PDFs and security/quality checks; publish through branch/PR/CI/merge/synchronization |
| Dependencies | Owner task-report-format addendum; finalized T3 and existing governance; authenticated GitHub access and documentation-only toolchain |
| Branch / baseline | `task/003-markdown-only-reporting`; `d1b575761c090c35dac535ec331a1e32f9bd5fe6` |
| Parent report | [Finalized T3](T3-Report.md), preserved unchanged; this addendum allocates no T4 |

## B. Implementation Summary

Updated root AGENTS.md and README.md, the report index, documentation library/build guide, acceptance criterion B14, and decision/change records DEC-19/CH-007. Every future task still needs its sequential finalized A–H Markdown report. This separate T3 addendum is Markdown only; no T4 was allocated.

Changed `scripts/build_docs.py` to exclude all of `reports/`, reject direct report rendering, and send report hyperlinks to Markdown/normal heading anchors. Changed `scripts/validate_docs.py` to require generated PDFs only outside that directory, reject new report PDFs, and accept the five optional existing archives only at their pinned baseline hashes. They are absent from the generated manifest and are never rebuilt. Updated workflow step descriptions and added five regression tests to the existing suite. Least-privilege permissions and the documentation-only dependency set remain unchanged.

Rebuilt nineteen active project-document editions and their manifest. Ten PDF binaries changed because of revised governance text or report-link destinations; the other nine active PDFs retained identical bytes. Visual review prompted wider change-history text columns so DEC-19/CH-007 and previous records remain readable. Preserved four finalized report Markdown files, five report/index PDF archives, and bootstrap evidence byte-for-byte. The project final report remains a template.

## C. Testing and Validation

| Check / executed command | Expected result | Actual observation | Status |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests -v` in the pinned documentation runtime | Existing behavior and new reporting cases pass | Thirty tests passed; coverage includes whole-directory exclusion/direct-render refusal, report-edit no-churn, Markdown report links, no PDF pairing, optional frozen archives, new/changed PDF rejection, and existing drift/security/history cases | PASS |
| `python scripts/build_docs.py` | Generate document PDFs only; preserve report archives | Nineteen active source/PDF pairs, 98 pages; no addendum PDF and no report PDF changes | PASS |
| `python scripts/build_docs.py --check --rebuild-check` | Source/manifest consistency and byte-identical fresh regeneration | All nineteen pairs passed; a no-change run skipped all nineteen outputs | PASS |
| `python scripts/validate_docs.py` and `git diff --check` | Links, A–H structure, numbering, traceability, publication patterns, workflow, archive hashes, and whitespace pass | Local checks passed; finalization gate and exact-head CI follow before merge | PASS |
| Git-baseline byte comparisons | Four finalized Markdown reports, five archived report PDFs, and bootstrap evidence unchanged | All compared with `d1b575761c090c35dac535ec331a1e32f9bd5fe6`; no historical differences | PASS |
| pypdf/pdfplumber inspection and Poppler rendering | Readable/searchable text, preserved navigation, no selected sensitive-data findings or clipping | Inspected generated text/metadata and character bounds; viewed all ten changed first pages, six detail samples, and the revised change-history page; corrected narrow history columns | PASS |
| Addendum PR, final exact-head CI, merge, and synchronization | Normal checked-head noreply merge; matching main refs | Pending publication at this draft checkpoint | NOT TESTED |

## D. Security and Quality Review

Retained selected secret/sensitive-data checks, approved binary publication, report structure/immutability checks, least-privilege CI, and manual public review. The archive exception is a fixed path/hash list from the published T3 baseline; it cannot admit new report PDFs, and archives are optional rather than required counterparts. Current report/index edits cannot silently regenerate old archives. Active document PDFs still require source hashes, approved manifest entries, fresh regeneration, and structural/text/navigation checks.

The initial Windows build could not update an assignment PDF held open by another application. A complete-file atomic replacement attempt also identified that lock; no file was truncated. The owner closed the PDF, then the standard build and checks succeeded. This was a resolved local environment issue. The change-history table's narrow columns were corrected and re-rendered during visual QA.

No lab, production, credential, account-privacy, license, or repository-protection change was performed. Operational security/isolation testing: NOT TESTED. Existing historical email metadata risk RK-17 remains an owner decision; no history rewrite was attempted.

## E. GitHub Operations

Authenticated account `waqashamdani-ca` has repository admin/push permission. Baseline local and remote main matched at `d1b575761c090c35dac535ec331a1e32f9bd5fe6`; worktree was clean. Addendum commit, PR, CI, merge, and final synchronization: pending.

## F. Outstanding Issues

Local implementation and validation are complete; publication/finalization read-back remains pending at this draft checkpoint. Existing historical email metadata risk RK-17 and prior owner decisions remain unchanged. Archive PDFs contain historical reporting instructions; current Markdown governance takes precedence. PDF reader-specific navigation and prior external-reference transport limits remain documented; no new external reachability or operational-security claim is made.

## G. Completion Status

| Area | Status |
| --- | --- |
| Engineering | IN PROGRESS |
| Independent verification | Git-baseline comparisons, separate PDF text/geometry/render observations completed; hosted CI pending; no independent human review claimed |
| Owner UAT | PENDING |
| Remaining owner decisions | Acceptance of the completed governance change; previously recorded privacy, protection, licensing, and future-stage decisions |

## H. Next Task

Stop after this T3 governance addendum. The recommended next bounded task remains a read-only Stage A hardware/isolation readiness assessment, requiring separate explicit owner approval and private evidence handling. No T4 or infrastructure implementation is authorized here.
