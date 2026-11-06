# Enterprise Zero Trust Security Architecture

HL-CYB-001 · Advanced cybersecurity engineering lab

## Project Overview

This project designs an isolated enterprise lab where people receive access to the systems needed for their role. It brings identity, network restrictions, certificates, logging, and recovery into one testable engineering assignment.

The scenario uses synthetic Purple Eye users and data, with no production or home-network connection.

## Business Problem

An employee may need to read a report without changing the application or administering its server. Remote access must let that employee reach the approved resource without opening the whole network.

The lab will demonstrate allowed and denied actions, access revocation, and the evidence behind each result. It makes no production-impact or compliance-certification claim.

## Project Objectives

- Design separate security zones and a protected administrative path using the available hardware.
- Give synthetic users and devices only the resource access required for their role.
- Test certificate trust, remote access, logging, automation, and recovery in individually approved stages.
- Publish reviewed engineering evidence and accurate task reports.

## Architecture Overview

Proxmox VE will run the virtual machines; OPNsense will control traffic between Management, Identity, Endpoints, Services, Monitoring, and Remote access zones. Active Directory manages lab identities; host/application permissions control resource access. An offline certificate authority protects the root of certificate trust.

Internet access needs a separately approved isolation design. See the [architecture](docs/architecture/ARCHITECTURE.md) for the diagram, capacity, and allowed flows, and the [glossary](docs/guides/GLOSSARY.md) for terms.

## Technologies Used

The repository currently uses **Git, GitHub, Python, and GitHub Actions** for version control and documentation checks.

Planned lab technologies are Proxmox VE, OPNsense, Windows Server Evaluation, Active Directory, DNS, Group Policy, Linux, public key infrastructure (PKI), Tailscale, Twingate, Ansible, and PowerShell. Their presence in the design does not mean they are installed or configured.

## Key Security Capabilities

Planned controls include access denied unless permitted, separate ordinary/admin identities, resource-scoped remote access, certificate issuance/revocation, central audit records, and encrypted backups with a timed restore. Each has a requirement and future test.

Production Microsoft 365 identities, PE-DAP, customer data, the corporate website, and production hosting, including AWS Lightsail, are excluded. Actual addresses, credentials, tenant details, raw logs, and backups stay outside public Git.

## Implementation Status

Repository setup, planning documents, task reporting, and documentation validation have been implemented and checked. **Lab implementation is PLANNED; operational controls are NOT TESTED.** Owner user acceptance testing (UAT) remains pending.

[T1](docs/reports/T1-Report.md) preserves the bootstrap results. [Its reporting addendum](docs/reports/T1-Addendum-001-Reporting-Governance.md) records the reporting migration. [T2](docs/reports/T2-Report.md) records the documentation review. No implementation stage starts without separate owner approval.

## Testing and Validation

Use Python 3.11 or later with the pinned [documentation dependencies](docs/governance/DOCUMENTATION-BUILD.md). With that documentation environment active:

```powershell
python scripts/validate_docs.py
python -m unittest discover -s tests -v
git diff --check
```

The checks cover documentation, local links, traceability, report history, and selected publication risks; they do not test the lab. Before completion, also run `python scripts/validate_docs.py --require-finalized`. Review public content manually: the scanner is not exhaustive, and CI does not fetch external references.

CI uses read-only permissions, a commit-pinned checkout, no retained credentials, and no lab access. The [test plan](docs/testing/TEST-PLAN.md) defines future functional, denied-access, security, and recovery checks.

## Project Documentation

Use the [documentation library](docs/README.md) for source/PDF pairs, including the [assignment PDF](docs/assignments/PROJECT-ASSIGNMENT.pdf), [lab guide PDF](docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.pdf), and [architecture PDF](docs/architecture/ARCHITECTURE.pdf). Markdown remains editable; PDFs are generated with the [documented Windows build](docs/governance/DOCUMENTATION-BUILD.md).

- [Assignment](docs/assignments/PROJECT-ASSIGNMENT.md): business case, requirements, deliverables, and assessment rubric.
- [Implementation guide](docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md): stages A–L, checks, rollback, and approval gates.
- [Architecture](docs/architecture/ARCHITECTURE.md) and [security requirements](docs/security/SECURITY-REQUIREMENTS.md): boundaries, access rules, threats, and standards mappings.
- [Acceptance criteria](docs/testing/ACCEPTANCE-CRITERIA.md), [decisions](docs/governance/DECISIONS.md), and [risks](docs/governance/RISKS.md): evaluation and unresolved choices.
- [Task reports](docs/reports/INDEX.md) and [bootstrap evidence](evidence/BOOTSTRAP-VALIDATION.md): work performed and evidence available.
- [Project final report template](docs/final-report/FINAL-REPORT.md), [glossary](docs/guides/GLOSSARY.md), and [references](docs/governance/REFERENCES.md): project assessment, terminology, and authoritative sources.

## Reporting and GitHub Workflow

Every task needs a sequential, finalized Markdown-only report (`docs/reports/Ti-Report.md`) before engineering completion. Reports and addenda do not receive PDFs; the entire reporting directory is excluded from PDF generation. Existing report PDFs are archived artifacts. Finalized Markdown reports remain immutable; corrections use an addendum or later task report. Owner UAT remains separate.

Use a task branch, focused commits, CI, and a reviewed pull request before merging; then fast-forward local `main`. Synchronization is intentional Git activity. [AGENTS.md](AGENTS.md) defines the workflow, approvals, writing standards, and prohibition on background upload. Protection/reviewer settings remain owner decisions.

## Author and Repository Information

Maintained under [waqashamdani-ca](https://github.com/waqashamdani-ca) in the public [enterprise-zero-trust-security repository](https://github.com/waqashamdani-ca/enterprise-zero-trust-security), with `main` as the default branch.

No software license has been selected. The recommended next task is T5: create the eight Word/Excel shells named in the assignment, after separate owner approval. Stage A hardware/isolation readiness remains the first infrastructure stage and needs its own approval.
