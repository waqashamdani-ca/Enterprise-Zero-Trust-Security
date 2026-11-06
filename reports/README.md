# Individual task reports

Every Codex task in HL-CYB-001 must create and finalize an individual report here. Reports explain what was authorized, what changed, how it was checked, what remains unresolved, and what may happen next. They are evidence records, not approval to begin another task.

## Index and numbering

| Task | Report | Scope |
| --- | --- | --- |
| T1 / Task 001 | [T1-Report.md](T1-Report.md) | Historical project bootstrap and GitHub setup |
| T1 addendum 001 | [Reporting governance](T1-Addendum-001-Reporting-Governance.md) | Migration and reporting rules; no Task 2 allocation |

Use `reports/T1-Report.md`, `reports/T2-Report.md`, and so on, without leading zeroes, gaps, or reuse. Before allocating a number, inspect the current local and remote reports and reconcile concurrent work. Do not create an empty report to reserve a number. The next report number does not authorize its task: obtain the owner's bounded scope first.

Corrections and additional evidence for an already finalized report go in a new file such as `T1-Addendum-002-Correction.md`. Addenda use a unique sequential three-digit number within their parent task and identify their reason. They do not change the parent task number or create a new task. Keep all individual reports and addenda here. [The project final report template](../docs/FINAL-REPORT.md) has a different purpose: the eventual assessment of the whole implemented project.

## Required A–H structure

Use the following headings exactly, with specific content under each one:

| Heading | Required content |
| --- | --- |
| A. Task Information | Task ID/title, execution date, authorized scope/objectives, and dependencies |
| B. Implementation Summary | Work completed, created/modified files, configuration changes, and important decisions |
| C. Testing and Validation | Tests actually performed, commands executed, expected versus observed results, and PASS/FAIL/NOT TESTED verdicts |
| D. Security and Quality Review | Security/publication checks, isolation verification if applicable, risks/findings, and remediation |
| E. GitHub Operations | Branch, verified commit SHA, PR if any, actual CI, merge status, and local/remote synchronization |
| F. Outstanding Issues | Known defects, limitations, risks, and dependencies |
| G. Completion Status | Engineering status, independent verification, owner UAT, and remaining owner decisions |
| H. Next Task | One recommended bounded task, prerequisites, and required owner approval |

Start with a descriptive title and `Report state: DRAFT`. In section A, include a table row named `Task ID` containing `T1`, `T2`, or the applicable parent ID. Use `## A. Task Information` through `## H. Next Task` for the eight sections. A report addendum uses the same structure.

Record tests as PASS, FAIL, or NOT TESTED, with evidence and an explanation. Separate project implementation status from task/report progress. Separate engineering verification, a second observation, independent human review, and owner UAT. Do not mark owner UAT PASS without an explicit owner confirmation reference. Missing data, future results, and an expected CI outcome are not evidence.

## Finalization and preservation

Create the draft during task execution. After the authorized implementation and validation are complete, review the evidence, record its cutoff and the finalization date, and change the marker to `Report state: FINALIZED`. From that point the report is immutable, including during later editing or readability work. Never edit, delete, overwrite, or renumber it. Use a new addendum for a correction or later outcome.

A report cannot contain the SHA of the commit that creates its own final bytes. Record verified implementation/test commits and the evidence cutoff. After publishing the report itself, read back its PR, CI, merge, and synchronization and include those results in the final task response or a later separate addendum. Distinguish pending publication at the cutoff from verified results; do not predict success.

Run `python scripts/validate_docs.py --require-finalized` before completion/merge. Focused checks cover file naming, sequence, A–H structure, and preservation of finalized report versions already in Git history. CI fetches complete history to support that check. This does not replace content/evidence review or GitHub protection settings. A task cannot be declared engineering-complete without its finalized report.

## T1 migration source

The original `docs/FINAL-REPORT.md` at bootstrap commit `4186787b153b2967381cffab353aaa81c72e6f70` is the authoritative source for [T1](T1-Report.md). Its exact UTF-8 content is retained in the report's source appendix, with a SHA-256 digest and immutable GitHub source link. Historical evidence files remain unchanged. The original task has no invented PR, owner acceptance, infrastructure result, or additional test claim.
