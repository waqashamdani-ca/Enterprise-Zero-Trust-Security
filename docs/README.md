# Documentation library

Markdown is the editable source. User-facing project documents have a generated PDF reading/printing edition; task reports are Markdown only. The [build guide](governance/DOCUMENTATION-BUILD.md) explains the Windows rebuild command, validation, and source/PDF consistency rules.

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

## Task reports and other instructions

[The task-report index](reports/INDEX.md) links the sequential Markdown-only reports and addenda. The entire `docs/reports/` directory, including its indexes, is excluded from PDF generation. Finalized Markdown remains immutable. Existing report PDFs are retained as historical archives and are not regenerated or required for later reports.

PDF editions also accompany the root [project overview](../README.pdf) and [agent governance](../AGENTS.pdf), [infrastructure guidance](../infrastructure/README.pdf), [configuration guidance](../configurations/README.pdf), [evidence handling](../evidence/README.pdf), and [bootstrap evidence](../evidence/BOOTSTRAP-VALIDATION.pdf). [This library index](README.pdf) is available as PDF too.

Compatibility pages under this directory preserve old decision/risk links and the relative links in relocated immutable reports. The aliases under `docs/docs/` and `docs/evidence/` point to maintained sources or unchanged evidence; they receive no PDFs. The manifest alias is a small JSON navigation record, not a duplicate manifest. The generated manifest lists every approved source/PDF pair and its content hashes.
