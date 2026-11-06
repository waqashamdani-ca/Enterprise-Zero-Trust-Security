# Documentation library

Markdown is the editable source for project documents, which have generated PDF reading/printing editions. The lab deliverable templates are editable Word/Excel files with no PDF editions; task reports are Markdown only. The [build guide](governance/DOCUMENTATION-BUILD.md) explains the Windows rebuild command, validation, and source/PDF consistency rules.

## Project documents

| Document | Source | PDF |
| --- | --- | --- |
| Project assignment specification | [Markdown](assignments/PROJECT-ASSIGNMENT.md) | [PDF](assignments/PROJECT-ASSIGNMENT.pdf) |
| Step-by-step lab implementation guide | [Markdown](lab-guides/LAB-IMPLEMENTATION-GUIDE.md) | [PDF](lab-guides/LAB-IMPLEMENTATION-GUIDE.pdf) |
| Architecture and design | [Markdown](architecture/ARCHITECTURE.md) | [PDF](architecture/ARCHITECTURE.pdf) |
| Security requirements | [Markdown](security/SECURITY-REQUIREMENTS.md) | [PDF](security/SECURITY-REQUIREMENTS.pdf) |
| Test plan | [Markdown](testing/TEST-PLAN.md) | [PDF](testing/TEST-PLAN.pdf) |
| Acceptance criteria | [Markdown](testing/ACCEPTANCE-CRITERIA.md) | [PDF](testing/ACCEPTANCE-CRITERIA.pdf) |
| Project final report template | [Markdown](final-report/FINAL-REPORT.md) | [PDF](final-report/FINAL-REPORT.pdf) |
| Decisions | [Markdown](governance/DECISIONS.md) | [PDF](governance/DECISIONS.pdf) |
| Risks | [Markdown](governance/RISKS.md) | [PDF](governance/RISKS.pdf) |
| Authoritative references | [Markdown](governance/REFERENCES.md) | [PDF](governance/REFERENCES.pdf) |
| Terminology and status | [Markdown](guides/GLOSSARY.md) | [PDF](guides/GLOSSARY.pdf) |
| Documentation build instructions | [Markdown](governance/DOCUMENTATION-BUILD.md) | [PDF](governance/DOCUMENTATION-BUILD.pdf) |

The final project report remains a clearly identified template. All infrastructure is PLANNED and its operational controls are NOT TESTED. No PDF adds implementation, certification, or owner acceptance claims.

## Editable lab deliverable templates

The [assignment](assignments/PROJECT-ASSIGNMENT.md#expected-deliverables) defines these five active blank templates. Complete them during approved lab work. Actual observations, execution dates, evidence, results and scores start empty; engineering tests start NOT TESTED and owner acceptance starts PENDING.

| Editable template | Requirements | Owning record |
| --- | --- | --- |
| [01 Environment and architecture](deliverables/01-Lab-Environment-and-Architecture.xlsx) | FWR-01, FWR-02 | Readiness/procurement separate from installation; four VMs, three zones, flows and capacity |
| [02 Identity and Zero Trust implementation](deliverables/02-Identity-and-Zero-Trust-Implementation.docx) | FWR-03 to FWR-06 | AD and separate application roles, endpoints, HTTPS, six cases and Tailscale/revocation summaries |
| [03 Security monitoring and testing](deliverables/03-Security-Monitoring-and-Testing.xlsx) | FWR-01 to FWR-10 | Five event categories, one denial investigation, ten tests/91 mandatory subchecks, coverage, one automation/restore, evidence and separate owner acceptance |
| [04 Troubleshooting and lessons](deliverables/04-Troubleshooting-and-Lessons.xlsx) | FWR-10 | One issue log with cause, correction, verification/retest and lesson |
| [05 Final project submission](deliverables/05-Final-Project-Submission.docx) | FWR-10 | Results summarized by reference, limitations, 100-point rubric and supporting deliverables |

Use Segoe UI answer areas and status dropdowns; add table rows when records grow. The testing workbook owns detailed execution so other files reference it. PASS requires every mandatory subcheck and evidence; blocked or missing work cannot become a passing test or an approved omission. Keep private working copies and originals outside Git and publish reviewed summaries only.

Run `python scripts/validate_office_templates.py` for bounded offline package/content checks. Native Microsoft Office editing, dropdown/filter behavior, recalculation and visual QA are separate observations recorded in [T7](reports/T7-Report.md); CI checks no lab control or owner acceptance. These editable files have no PDF editions.

The eight verified blank T5 shells were retired by normal Git changes. Their complete [original template directory](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/tree/6f5352bb6d5e2eca37ac2384703367543530b952/docs/deliverables) and [T5 report snapshot](https://github.com/waqashamdani-ca/Enterprise-Zero-Trust-Security/blob/6f5352bb6d5e2eca37ac2384703367543530b952/docs/reports/T5-Report.md) preserve historical links and definitions. Old targets/results do not govern this baseline. Finalized reports remain unchanged.

## Task reports and other instructions

[The task-report index](reports/INDEX.md) links the sequential Markdown-only reports and addenda. The entire `docs/reports/` directory, including its indexes, is excluded from PDF generation. Finalized Markdown remains immutable. Existing report PDFs are retained as historical archives and are not regenerated or required for later reports.

PDF editions also accompany the root [project overview](../README.pdf) and [agent governance](../AGENTS.pdf), [infrastructure guidance](../infrastructure/README.pdf), [configuration guidance](../configurations/README.pdf), [evidence handling](../evidence/README.pdf), and [bootstrap evidence](../evidence/BOOTSTRAP-VALIDATION.pdf). [This library index](README.pdf) is available as PDF too.

Compatibility pages under this directory preserve old decision/risk links and the relative links in relocated immutable reports. The aliases under `docs/docs/` and `docs/evidence/` point to maintained sources or unchanged evidence; they receive no PDFs. The manifest alias is a small JSON navigation record, not a duplicate manifest. The generated manifest lists every approved source/PDF pair and its content hashes.
