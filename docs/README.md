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

The [assignment](assignments/PROJECT-ASSIGNMENT.md#expected-deliverables) defines the five approved future T7 filenames. They are not yet created. T7 requires separate owner approval to reconcile the eight existing files below.

These are **legacy T5 blank shells**, byte-preserved in T6. Their old requirements, counts, rubric and stage prompts describe the retired baseline and do not govern current implementation. Do not use them as current answer sheets until approved T7 migration. Their original actual/evidence fields remain empty.

| Editable template | Historical requirements | Historical T5 purpose |
| --- | --- | --- |
| [01-Lab-Environment.xlsx](deliverables/01-Lab-Environment.xlsx) | R02 | Hardware, VMs, software, stage checklist and planned/actual resource ledger |
| [02-Architecture-and-Network-Design.docx](deliverables/02-Architecture-and-Network-Design.docx) | R01, R03, R04, R15 | Business roles, zones, diagrams, flows, threats, decisions and limitations |
| [03-Identity-and-Access-Management.xlsx](deliverables/03-Identity-and-Access-Management.xlsx) | R05, R06, R08 | Synthetic identities, groups, permissions, authentication, privilege, endpoint baselines and revocation timing |
| [04-Zero-Trust-Implementation.docx](deliverables/04-Zero-Trust-Implementation.docx) | R03, R04, R07, R09, R12, R13 | Stage A-L configuration references, certificate lifecycle, sequential pilots, two automations and recovery procedures |
| [05-Security-Monitoring.xlsx](deliverables/05-Security-Monitoring.xlsx) | R10 | Log sources, twenty event timestamps, detections, investigations, coverage, clock offsets and retention sizing |
| [06-Testing-and-Validation.xlsx](deliverables/06-Testing-and-Validation.xlsx) | R01, R13, R14 | All R01-R16 mappings and T00-T20 definitions, individual cases, actual results/evidence, recovery measurements, exceptions and separate owner UAT |
| [07-Troubleshooting-and-Lessons.xlsx](deliverables/07-Troubleshooting-and-Lessons.xlsx) | R14, R15 | Issues, impact, investigation, correction/rollback, verification and lessons |
| [08-Final-Lab-Submission.docx](deliverables/08-Final-Lab-Submission.docx) | R11, R15, R16 | Assessment, supporting-file references, measured-outcome summary, rubric, public hygiene and GitHub record |


Run `python scripts/validate_office_templates.py` to inspect the unchanged legacy packages. Native Office/layout validation belongs to [T5](reports/T5-Report.md); T6 does not reopen, edit or regenerate these files. Keep future working records private.

## Task reports and other instructions

[The task-report index](reports/INDEX.md) links the sequential Markdown-only reports and addenda. The entire `docs/reports/` directory, including its indexes, is excluded from PDF generation. Finalized Markdown remains immutable. Existing report PDFs are retained as historical archives and are not regenerated or required for later reports.

PDF editions also accompany the root [project overview](../README.pdf) and [agent governance](../AGENTS.pdf), [infrastructure guidance](../infrastructure/README.pdf), [configuration guidance](../configurations/README.pdf), [evidence handling](../evidence/README.pdf), and [bootstrap evidence](../evidence/BOOTSTRAP-VALIDATION.pdf). [This library index](README.pdf) is available as PDF too.

Compatibility pages under this directory preserve old decision/risk links and the relative links in relocated immutable reports. The aliases under `docs/docs/` and `docs/evidence/` point to maintained sources or unchanged evidence; they receive no PDFs. The manifest alias is a small JSON navigation record, not a duplicate manifest. The generated manifest lists every approved source/PDF pair and its content hashes.
