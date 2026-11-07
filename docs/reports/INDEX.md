# Task reports and reporting convention

Use this index for the current location and reporting rules. Every task in HL-CYB-001 requires a sequential Markdown-only report in `docs/reports/`. Reports describe authorization, changes, actual checks, remaining issues and the next bounded task; they do not authorize further work. This entire directory, including both indexes and nested files, is excluded from PDF generation.

## Reports

| Task | Record | Scope |
| --- | --- | --- |
| T1 / Task 001 | [T1 report](T1-Report.md) | Project bootstrap and GitHub setup |
| T1 addendum 001 | [Reporting governance](T1-Addendum-001-Reporting-Governance.md) | Reporting migration and rules |
| T2 | [T2 report](T2-Report.md) | Documentation quality and readability |
| T3 | [T3 report](T3-Report.md) | Documentation organization and PDF editions |
| T3 addendum 001 | [Markdown-only reporting](T3-Addendum-001-Markdown-Only-Reporting.md) | PDF exclusion and reporting governance |
| T4 | [T4 report](T4-Report.md) | Assignment redesign, submission filenames and report-folder migration |
| T5 | [T5 report](T5-Report.md) | Eight editable Word/Excel lab deliverable shells and their validation |
| T6 | [T6 report](T6-Report.md) | Four-week project specification/PDF alignment and ordered-hardware status; Office files unchanged |
| T6A | [T6A report](T6A-Report.md) | Owner-authorized assignment language/design/layout follow-up; T6 scope preserved |
| T6B | [T6B report](T6B-Report.md) | Owner-authorized Lab Guide usability/language/layout follow-up; T6 scope preserved |
| T7 | [T7 report](T7-Report.md) | Five four-week Office deliverables, legacy retirement, native/visual validation and publication |
| T8 | [T8 report](T8-Report.md) | Practical Lab Guide rewrite, instructional/PDF redesign, full editorial/visual validation and publication |

## Numbering and required content

Use `docs/reports/T1-Report.md`, `docs/reports/T2-Report.md`, and subsequent numbers without gaps, reuse or renumbering. Inspect local and remote work before allocation. A new number does not authorize a task. Corrections to finalized records use a separately numbered addendum such as `T4-Addendum-001-Correction.md`, with the same parent task ID and no new task number.

The owner explicitly authorized `T6A-Report.md` and `T6B-Report.md` as companions to finalized T6, using their respective Task IDs. Both preserve the same A-H/finalization/history rules; neither allocates T7 nor authorizes other lettered tasks. T6B depends on completed T6A publication.

Start with a descriptive title and `Report state: DRAFT`. Include a `Task ID` table row in section A. Use these headings exactly, once and in order:

| Heading | Required content |
| --- | --- |
| A. Task Information | Task ID/title, dates, approved scope, objectives and dependencies |
| B. Implementation Summary | Changed files/configuration, completed work and decisions |
| C. Testing and Validation | Executed commands, expected/actual results, evidence and PASS/FAIL/NOT TESTED verdicts |
| D. Security and Quality Review | Publication/safety checks, findings, risks and remediation |
| E. GitHub Operations | Branch, verified commits, PR, actual CI/merge and synchronization |
| F. Outstanding Issues | Defects, limitations, unresolved risks and dependencies |
| G. Completion Status | Engineering, second observations, independent human review and separate owner UAT |
| H. Next Task | One bounded recommendation with explicit approval requirements |

Finalize only after reviewing actual evidence. Record the evidence cutoff and finalization date, then use `Report state: FINALIZED`. A finalized report is immutable; later evidence needs an addendum or subsequent authorized report. Never predict its own commit SHA, future CI/merge or owner acceptance. Verify publication after finalization and report those observed results in the final chat response. Run `python scripts/validate_docs.py --require-finalized` before completion or merge.

Owner UAT remains PENDING without an explicit confirmation reference. A second observation is not a second human reviewer. Repository checks do not validate lab controls or approve the next stage. The [project final report](../final-report/FINAL-REPORT.md) is a separate project-level template and retains its PDF edition.

## Historical preservation and navigation

T4 moved all eleven existing files from the root report folder without changing their bytes, including the [original index](README.md). That index's paths and instructions describe the earlier location; this index and [AGENTS.md](../../AGENTS.md) define the current convention. The five historical PDFs remain frozen archives, excluded from builds and the generated manifest. No new task report, addendum or index receives a PDF.

Relative links inside immutable files are preserved through small navigation aliases under `docs/docs/` and `docs/evidence/`. They point to maintained documents or unchanged evidence; they are not duplicate report/source editions and receive no PDFs. The manifest alias is a JSON navigation record with a current target URL. Commit-specific GitHub links still describe their original evidence snapshots. The validator checks both historical report paths, exact file hashes and current links, and rejects duplicate report locations.

T5 Office links refer to files retired by T7. Open the [original T5 report snapshot](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/blob/6f5352bb6d5e2eca37ac2384703367543530b952/docs/reports/T5-Report.md) for its working historical relative links. The validator resolves only that immutable report's eight retired targets against the verified published snapshot; it does not permit missing active-template links.

The original bootstrap report source remains preserved in T1's source appendix and its immutable GitHub reference. No historical evidence or Git history was rewritten.
