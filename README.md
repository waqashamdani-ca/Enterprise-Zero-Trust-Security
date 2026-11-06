# Enterprise Zero Trust Security Architecture

**HL-CYB-001 · Advanced cybersecurity engineering lab · Task 001: planning and repository bootstrap**

Design an isolated, virtual enterprise to study identity, least privilege, segmentation, PKI, remote access, monitoring, and recovery. The business scenario uses a synthetic Purple Eye environment. This is an independent educational project; it has no production trust, corporate identities, customer data, or production connectivity.

The repository contains a proposed architecture, an engineering assignment, an approval-gated implementation blueprint, and documentation validation. A published repository or passing documentation CI is not evidence that the lab exists or its security controls work.

## Start here

| Document | Purpose |
| --- | --- |
| [Project assignment](docs/PROJECT-ASSIGNMENT.md) | Business case, measurable requirements, deliverables, and 100-point rubric |
| [Implementation guide](docs/LAB-IMPLEMENTATION-GUIDE.md) | Proposed stages A–L, verification, rollback, and owner gates |
| [Architecture](docs/ARCHITECTURE.md) | Resource budget, trust boundaries, allowed flows, and isolation design |
| [Security requirements](docs/SECURITY-REQUIREMENTS.md) | Threat model and tailored NIST/CIS mappings |
| [Test plan](docs/TEST-PLAN.md) | Future functional, negative, security, and recovery validation |
| [Acceptance criteria](docs/ACCEPTANCE-CRITERIA.md) | Bootstrap acceptance and future engineering/UAT gates |
| [Decisions](docs/DECISIONS.md) | Proposed decisions, outstanding owner choices, and change history |
| [Risks](docs/RISKS.md) | Constraints, mitigations, and residual risk |
| [Task reports](reports/README.md) | Individual, sequential reports and the reporting convention |
| [Task 1 report](reports/T1-Report.md) | Preserved Task 001 outcomes and evidence |
| [Project final report template](docs/FINAL-REPORT.md) | Project-wide assessment to complete after approved implementation |
| [References](docs/REFERENCES.md) | Authoritative sources and command verification references |
| [Agent governance](AGENTS.md) | Execution boundaries and repository conventions |

## Scope and safety

Task 001 authorizes documentation, scaffolding, local Git initialization, and reviewed publication to the public [GitHub repository](https://github.com/waqashamdani-ca/enterprise-zero-trust-security). It does not authorize installing software, provisioning VMs, changing networks, deploying identity services, or running security tests.

All later stages require explicit owner approval for that individual stage. Use lab-only identities and synthetic data. Corporate Microsoft 365, PE-DAP, the corporate website, and current or future production hosting, including AWS Lightsail, are excluded. Never connect a lab domain, PKI, remote-access tenant, or automation identity to production.

The public design uses symbolic network addresses. Actual lab addresses, home network details, vendor tenant identifiers, raw logs, backups, and credentials belong in private owner-controlled storage outside the repository. Google Wifi is treated only as an existing home network; the design does not depend on changing it or assuming enterprise VLAN capabilities.

## Repository layout

```text
.github/workflows/        Documentation-only CI
docs/                    Assignment, design, requirements, guide, and status
infrastructure/          Future reviewed infrastructure definitions
configurations/          Future sanitized configuration examples
scripts/                 Local documentation validation
tests/                   Focused tests of the documentation validator
evidence/                Reviewed, sanitized evidence and capture conventions
reports/                 Individual task reports and historical addenda
```

No infrastructure or production configuration is included in the bootstrap.

## Validate documentation

Use an already available Python 3.11 or later installation; these commands do not install dependencies or contact the lab:

```powershell
python scripts/validate_docs.py
python -m unittest discover -s tests -v
git diff --check
```

The standard-library validator checks required structure, local Markdown destinations and heading anchors, stage completeness, requirement traceability, rubric totals, and selected public-publication risks. It scans Git's proposed tracked/untracked, nonignored file set and rejects sensitive filenames, binary artifacts, private addresses, and selected credential patterns. It is a focused guardrail with known limits; a manual review of staged contents remains mandatory. External references are checked during bootstrap research, not fetched on every CI run.

The workflow uses read-only repository permissions, an official checkout action pinned to a verified commit, no stored checkout credentials, no deployment jobs, and no lab secrets or remote-access connection.

## Task reporting

Every task must produce a report in `reports/`: `T1-Report.md`, `T2-Report.md`, and the next unique sequential number. Reports record scope, changes, executed tests and actual results, security review, GitHub operations, unresolved issues, completion/UAT status, and the next task's prerequisites and approval. A task is not engineering-complete until its report is finalized.

Drafts use `Report state: DRAFT`; finalized reports use `Report state: FINALIZED` and become immutable. Corrections and later evidence go in a separate addendum or the next authorized task's report. The [reporting guide](reports/README.md) defines the A–H structure. Owner UAT remains pending until the owner explicitly accepts the work. Before completion, run `python scripts/validate_docs.py --require-finalized`. The project final report template summarizes the eventual project and does not hold individual task reports.

## GitHub workflow

The owner account is `waqashamdani-ca`; the repository is public, and the default branch is `main`. After the reviewed bootstrap, use a branch such as `task/002-hardware-readiness` for each bounded engineering task. Make focused commits, push that branch, run relevant checks, and open a pull request. Review engineering evidence and obtain the required owner approval before merging. Document UAT separately from engineering verification.

Start future work from a clean, synchronized `main`:

```powershell
git switch main
git pull --ff-only origin main
git switch -c task/002-hardware-readiness
```

After reviewing changes, stage explicit paths, inspect `git diff --cached`, run the local checks, commit, and push with `git push -u origin task/002-hardware-readiness`. Open a PR with the problem, scope, verification, risks, rollback, and owner approval record. After a reviewed merge, synchronize local `main` with another fast-forward-only pull. Stop on divergence and reconcile through a reviewed branch. Never force-push, reset away work, or overwrite an existing repository without explicit approval.

Synchronization consists of intentional commits, pushes, PRs, and pulls. It is not background upload or automatic transmission of local files. Inspect `git remote -v`, `git status`, `git branch -vv`, `git log -1`, and `git ls-remote origin` when confirming synchronization. Branch protection and required reviewers are an open owner decision; documented conventions alone do not enforce them.

## Current next task

Owner review of Task 001, followed by a separately approved, read-only **Stage A hardware and isolation readiness assessment**. No installation or Project Stage 1 work begins as part of this bootstrap.

## License

No software license has been selected. Public visibility does not establish an open-source license; the owner must approve licensing before a license file is added.
