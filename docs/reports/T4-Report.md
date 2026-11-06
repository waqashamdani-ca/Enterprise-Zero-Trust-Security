# T4 - Project assignment redesign, submission filenames and report-folder migration

Report state: FINALIZED

Evidence cutoff: 2026-11-06 07:37:45 UTC (2026-11-06, America/Toronto). Finalization date: 2026-11-06, America/Toronto. Later report-commit CI, merge and final synchronization are outside this cutoff.

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T4 |
| Execution date | 2026-11-06, America/Toronto |
| Authorized scope | Redesign the assignment Markdown/PDF; finalize eight future Word/Excel submission filenames; relocate the complete report folder without byte changes; update affected navigation/build/checks/tests/CI; publish by PR and synchronize main |
| Approval reference | Owner T4 assignment-redesign request and report-relocation/deliverable-filename addenda, 2026-11-06; private originals retained by owner |
| Baseline | Clean main at 0d28d105a517606e7a0a1cdaf4939f166b2f3a53; local and remote main matched; git pull --ff-only origin main reported already up to date |
| Dependencies | Existing pinned documentation runtime and Poppler; no software installed; supported GitHub authentication and repository write access verified |
| Status at evidence cutoff | Local implementation/verification complete; implementation commit published and initial push/PR CI successful; report-finalization commit, final-head CI, merge and main synchronization pending |

The design review covered the assignment, architecture, security/threat requirements, tests, acceptance, decision/risk registers, reporting convention and PDF build. The measurable T4 outcomes are a concise readable assignment, unchanged R01-R16/rubric obligations, eight unique filenames covering all outcomes, eleven byte-preserved migrated files, working navigation, Markdown-only reporting and reproducible document PDFs. Threat/control changes are out of scope; public disclosure and broken historical navigation are the relevant risks.

Rollback: use a normal reviewed revert of T4 code/current-document changes and inverse file moves, preserving finalized report bytes. Reconcile the authorized path convention before any revert; do not delete finalized records, rewrite published history or force-push. No lab or production operation is involved.

## B. Implementation Summary

The assignment now leads with the business scenario, then uses nine sections: overview, objectives, scope, technologies/resources, requirements, deliverables, implementation approach, success criteria and references. It decreased from 2,892 to 1,922 whitespace-delimited words and from ten to six PDF pages, including its cover. The source remains authoritative.

Consolidated repeated scenario/purpose/governance explanations, prerequisite/dependency narrative, component descriptions and testing instructions. Removed the introductory metadata table, duplicated implementation alternatives, a separate publication procedure and speculative resume-achievement section. Detailed topology, threat/control mappings, stage procedures, official vendor references and acceptance gates remain linked in their authoritative documents. No requirement, rubric category/weight, security boundary or required future outcome was removed.

The assignment alone receives a cover with linked contents, 10-point body text, restrained blue/gray headings, simpler table rules and a filename column that fits each full name. Fonts, deterministic metadata, source-derived versions, headers/footers, repeated table headers, clickable links and named heading destinations are retained. Other renderer styles are unchanged.

The entire root report directory moved to docs/reports/. All eleven prior files, including the old README and five historical PDFs, remain byte-identical. A new [current index](INDEX.md) gives the active paths and convention; the frozen README preserves the owner's requested complete file contents. Small navigation aliases under docs/docs/ and docs/evidence/ preserve relative links in immutable files. The manifest alias is a JSON navigation record, not a duplicate generated manifest. There is no report copy at the old root location.

Build discovery/direct rendering exclude both new and legacy report paths. Validation now checks the authorized relocation across both Git-history locations, raw bytes including newline changes, every migrated file hash, missing/duplicate locations, Markdown-only reports, aliases and submission filenames/formats/coverage. Focused tests retain the earlier public-hygiene/PDF checks and add relocation, rubric/guide preservation and assignment-layout checks. CI remains read-only, full-history, commit-pinned and without lab access.

Changed artifact groups:

- Assignment source/PDF and documentation manifest.
- Root README/AGENTS, documentation library, governance build/decision/risk documents and their generated PDFs.
- Lab-guide introductory navigation and report links; acceptance/test/final-template report links and corresponding PDFs.
- Report relocation, new current index and this Markdown-only report; six navigation aliases with no PDF editions.
- scripts/build_docs.py, scripts/validate_docs.py, both focused test files and documentation workflow step descriptions.

Decisions DEC-20/DEC-21 and change CH-008 record the assignment/submission baseline and path-only report move. RK-19 records the historical-navigation risk. No license, repository-protection setting or lab architecture was selected or changed.

### Finalized submission filenames

All files belong in docs/deliverables/. They are specified only; no Word/Excel shells were created in T4. The lab guide links this single list instead of duplicating it.

| Filename | Format | Requirements covered |
| --- | --- | --- |
| 01-Lab-Environment.xlsx | Excel (.xlsx) | R02 |
| 02-Architecture-and-Network-Design.docx | Word (.docx) | R01, R03, R04, R15 |
| 03-Identity-and-Access-Management.xlsx | Excel (.xlsx) | R05, R06, R08 |
| 04-Zero-Trust-Implementation.docx | Word (.docx) | R03, R04, R07, R09, R12, R13 |
| 05-Security-Monitoring.xlsx | Excel (.xlsx) | R10 |
| 06-Testing-and-Validation.xlsx | Excel (.xlsx) | R01, R13, R14 |
| 07-Troubleshooting-and-Lessons.xlsx | Excel (.xlsx) | R14, R15 |
| 08-Final-Lab-Submission.docx | Word (.docx) | R11, R15, R16 |

## C. Testing and Validation

Results below are documentation engineering checks, not executed lab tests. The verifier was Codex. PDF commands used the existing bundled Python 3.12.14 with exactly the requirements-docs.txt versions; python below denotes that interpreter for build/test commands. The standard-library validator also ran with the existing default Python. No dependencies were installed.

| Check / executed command | Expected | Actual / verdict |
| --- | --- | --- |
| Baseline Git status/remotes/branches/log; git pull --ff-only origin main; remote branches and open-PR inspection | Clean current main; no allocated T4/concurrent PR | Clean synchronized baseline; no T4 branch/report or open PR before allocation. PASS |
| git/gh identity and repository API inspection | Correct account, write permission, PUBLIC/main; known protection/merge rules | Authorized owner account; admin/push permission; main unprotected, no effective rules; normal merge allowed. Both local identity fields use the owner's verified noreply email. PASS |
| python scripts/build_docs.py | Faithful document outputs; no report generation | 19 maintained source/PDF pairs, 95 pages total; assignment six pages. All report/index/alias sources excluded. PASS |
| python scripts/build_docs.py --check --rebuild-check | Hash/structure/content/link checks and fresh byte-identical generation | 19 pairs unchanged, zero generated; deterministic fresh bytes match. PASS |
| python scripts/validate_docs.py | Required structure, links/anchors, numbering/history, migration hashes, traceability, public scan | 68 candidates, 34 Markdown files; all checks passed. PASS |
| python -m unittest discover -s tests -v | Existing and new positive/negative regressions pass | All 38 tests passed; temporary Windows fixture access requires the authorized normal-access run. PASS after correction of the cover-contents orphan-heading false positive |
| git diff --check; git diff --cached --check | No whitespace errors | No findings. PASS |
| Historical file comparison with pre-T4 Git blobs and saved SHA-256 inventory | All eleven relocated files identical, old directory absent, no report copies | All eleven hashes identical; five archived PDFs unchanged; original source appendix/bootstrap evidence preserved. PASS |
| Guide stage-body comparison against pre-T4 Git bytes | No substantive stage A-L edits | Byte-identical from the Stage A heading through Stage L; only introductory navigation/report references changed. PASS |
| Assignment requirement/deliverable/rubric review and regression checks | R01-R16 once; all outcomes mapped; eight unique correct Office names; original eleven scores | Complete R01-R16 coverage; all eight names unique and formats match; all rubric labels/weights match baseline exactly, total 100. PASS |
| Poppler rendering; visual inspection of assignment pages 1-6 and representative related PDFs | Readable type, complete names/tables, correct page numbers, no clipping/overlap/missing glyphs | Every assignment page inspected after final content/layout change; representative pages from all ten other changed documents inspected, including the latest acceptance/decision/build-guide revisions. PASS |
| pypdf inspection independent of PNG rendering | Searchable content, preserved links and navigation; no executable content | Assignment text-token coverage 1.0, ten named destinations, eighteen internal link annotations and twelve unique HTTPS links; no script/attachment/form. PASS |
| NIST 800-207, NIST 800-53 Rev. 5 and CIS v8.1 primary-page reads | Essential external reference pages accessible | All three official pages opened on 2026-11-06; project destinations/anchors checked locally. PASS; no lab/vendor procedure was executed |
| T5 Office-shell/infrastructure execution check | No templates or lab changes | No docs/deliverables/ artifacts, new report PDFs, installation, VM/network/identity change or security test. PASS for scope control; lab controls NOT TESTED |

Initial restricted tests failed to access temporary Windows fixtures; the normal-access run resolved that environment limit. A new regression found that the cover's contents list was being mistaken for an orphan heading; the check now recognizes the assignment contents page while retaining ordinary orphan-heading checks. A migrated library link was also corrected before the successful validation. No check was disabled and no publication finding was bypassed.

### Requirement preservation

| Requirements | Preserved obligation / supporting detail |
| --- | --- |
| R01-R04 | Zero protected-network paths/trust/data; measured hardware and 248 GiB/36 GiB ceilings; dedicated administration/MFA/console; six zones with justified permits/default deny |
| R05-R08 | Separate forest/DNS/policy, six users/three groups/two privileged accounts; Windows/Linux baselines; offline root/separate issuer and application certificate lifecycle; twelve same-zone-inclusive access cases and fifteen-minute revocation target |
| R09-R10 | Sequential separate Tailscale/Twingate pilots, MFA/one resource/deny/revocation and no broad routes; six event classes, at least 19/20 searchable within five minutes, two-second clocks and thirty-day capacity design |
| R11-R13 | Reviewed public artifacts/history with no secrets/sensitive records; two automations with zero unintended repeat-run changes; encrypted off-compute timed restore with 24-hour/four-hour recovery targets |
| R14-R16 | All approved mandatory tests, 100% critical/95% applicable noncritical, no high-severity issue and separate owner UAT; complete traceable documentation; reviewed public Git/PR/CI and synchronized main |

The unchanged test plan retains T00-T20 and the requirement coverage/stage mapping. Security requirements retain the threat register and NIST/CIS control mappings. Detailed commands remain in the guide, where their proposed status and stage approval boundaries are unchanged. Neither planning checks nor this review establish operational control success.

### Migration evidence

The following SHA-256 values match both the pre-T4 baseline Git blobs and the current files in docs/reports/. The validator pins the complete set.

| Migrated filename | SHA-256 |
| --- | --- |
| README.md | b1db4ef489bd607171966fc5dc1f81778374b95cd3a3946018f09220add2e7ed |
| README.pdf | 8dac0d69a194a43a550f086e409cb763245bbd583d9e1e1fe94db6bb933d6567 |
| T1-Addendum-001-Reporting-Governance.md | 792d74c5dd486cb1ceea0a639d46d585f6b3576402476624125cfd3239c0689e |
| T1-Addendum-001-Reporting-Governance.pdf | e684fa1f73c0cf8aa9029dc0ae13c2fbab3bb1c26a77ae5a00925d5d5f3bde56 |
| T1-Report.md | 428c869a9c4c3d2d5b7e03881b719a264690e515256214514b25fe2c46a4fca6 |
| T1-Report.pdf | c42f42e0b548c0996a66f6431da09fcf85995dd5e0841b9358e58f01fb206dd9 |
| T2-Report.md | 6ffbf30e74f5456c7b2b4f78555722a98dfabac97475367fd16adbe84e8c9dab |
| T2-Report.pdf | 36ec642bee80564ac9e50bb5c24900211f70908d5a2fb29d6c51f26d2d6e5856 |
| T3-Addendum-001-Markdown-Only-Reporting.md | 502cee8541f417263e008a9205e71c7cab27fcca05e1ad9d8067e140a2289ea8 |
| T3-Report.md | e5542bbdef113b8debc45150dc33b78586105c7492227ea4e3c8033e1135f761 |
| T3-Report.pdf | 4ab8ce03f2009e8cfbfe44c4b9803780043f3b7203b7373cb0f1aa64e3a8ab5d |

Eight unaffected document PDFs, including architecture, security requirements, references, glossary and bootstrap evidence, remain byte-identical to the baseline. Eleven document PDFs changed because the assignment, authorized migration references or T4 governance records changed. No frozen report PDF was rebuilt. Raw logs, baseline inventories and preview images remain in ignored local/tmp locations and are not published.

## D. Security and Quality Review

Manual review covered the complete candidate paths, staged text/code changes, PDF metadata/content and new commit history before initial publication. The staged-diff and new-history focused scans passed. Automated scanning supports that review but is not a complete secret detector. Public examples remain synthetic/reserved; no credentials, actual internal addresses, private inventory, raw evidence or proprietary content was introduced. No background upload, production access, lab probes or new trust occurred.

The workflow retains contents: read, full-SHA official checkout, fetch-depth: 0 and persist-credentials: false. It runs documentation checks only. Existing non-noreply metadata findings remain RK-17; T4 does not rewrite history. New commits and the planned local merge must verify both author/committer noreply fields.

Independent observations comprise Git/remote read-back, baseline raw-hash comparisons, PDF text/navigation inspection and separate PNG visual review. These are engineering observations by the same verifier. Independent human review and owner UAT are not claimed. RK-19's remaining navigation hop is documented in the current index; current documents link directly to maintained paths.

## E. GitHub Operations

| Item | Observed state at evidence cutoff |
| --- | --- |
| Repository | [waqashamdani-ca/Enterprise-Zero-Trust-Security](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security), PUBLIC, default main; repository ID 1447671295 |
| Authenticated account / permission | waqashamdani-ca; push/admin verified with connector and GitHub CLI/API |
| Branch | task/004-assignment-redesign |
| Dependency baseline | 0d28d105a517606e7a0a1cdaf4939f166b2f3a53, clean/synchronized before branch creation |
| Verified implementation commit | [f08a8d44f1c174a77cf54a622c470a92d0808222](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/commit/f08a8d44f1c174a77cf54a622c470a92d0808222); both author/committer verified noreply; new-history scan passed |
| Pull request | [PR 5](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/pull/5), OPEN and mergeable/CLEAN at cutoff, exact head f08a8d44f1c174a77cf54a622c470a92d0808222; no submitted reviews or review threads |
| Actual CI | [Push run 42181713894](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/actions/runs/42181713894) and [PR run 42181862000](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/actions/runs/42181862000): completed / success at the implementation head; all PR validation job steps successful |
| Branch synchronization | git ls-remote confirmed the T4 branch at f08a8d44f1c174a77cf54a622c470a92d0808222 and remote main at baseline 0d28d105a517606e7a0a1cdaf4939f166b2f3a53 |
| Merge and final main synchronization | Pending report-finalization publication and exact-final-head checks; not claimed at cutoff |

GitHub reported a case-only repository rename during the first push. The connector confirmed the same repository ID, account, permissions, visibility and default branch; the configured lowercase origin remains a working redirect. T4 did not rename the repository or change origin. The connected integration returned 403 for PR creation; the existing authenticated GitHub CLI successfully created PR 5 using a reviewed body file, and connector/CLI reads independently confirmed it.

No protection, reviewer setting or account privacy setting changed. A normal local merge with verified noreply author/committer is planned only after exact-final-head CI and all applicable review/protection requirements pass; GitHub's merged state and local/remote main must then be read back. These later outcomes belong in the final chat response. Permission to merge is not owner acceptance.

## F. Outstanding Issues

Publication/CI of the report-finalization commit, final PR merge and main synchronization remain outside this cutoff. No unresolved assignment, relocation or local-check defect is known after correction. Existing implementation decisions remain open: inspected hardware/disk/backup readiness, isolated egress, supported versions/evaluation terms, provider identities/plans, log transport/retention and recovery scope. Licensing, repository rules/reviewers and historical metadata remediation remain owner decisions. None blocks the bounded documentation result or authorizes implementation.

The old report index is intentionally byte-frozen; use INDEX.md for current instructions. Compatibility aliases are navigation records, and some historical Markdown links take that extra step. Archived PDFs retain their historical text and URLs, including old report paths; use the current index/Markdown for navigation rather than altering archive bytes. A PDF viewer may handle external named destinations differently; current document destinations and embedded URLs passed structural checks. The standard-library scanner and text-token coverage do not replace manual review.

## G. Completion Status

| Dimension | State |
| --- | --- |
| Local documentation implementation | VALIDATED for the documentation scope; engineering checks passed |
| Report state / publication | FINALIZED at this cutoff; implementation publication/initial CI verified; final report publication, merge and main synchronization still pending |
| Independent observations | PASS for scope described in C/D; same engineering verifier |
| Independent human reviewer sign-off | NOT TESTED / not performed |
| Owner UAT | PENDING; no explicit acceptance reference received |
| T5 shells | NOT STARTED; filenames defined only |
| Lab stages A-L | PLANNED / NOT TESTED; not authorized by T4 |

This report is finalized after review of the local evidence, published implementation commit and successful initial push/PR CI. The required python scripts/validate_docs.py --require-finalized gate will run against these final bytes before completion/merge. Its post-cutoff result, the finalization commit SHA, later CI, merge and synchronization must be reported after observation in the final chat response. This record makes no prediction about those outcomes.

## H. Next Task

Recommend T5 only: create the eight editable Microsoft Word/Excel submission shells named in the assignment. Obtain explicit owner approval for those eight files, their structure, location, validation and publication/reporting scope before creation. Do not begin infrastructure; Stage A still needs its own asset/scope/validation/rollback approval. T4 stops after final reporting, checked PR merge and main synchronization, awaiting owner review.
