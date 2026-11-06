# Enterprise Zero Trust Security Architecture

HL-CYB-001 | Four-week focused cybersecurity lab

A synthetic analyst needs report access, an engineer needs maintenance instructions and an unassigned user must be denied. This project designs a small isolated lab to demonstrate those decisions, remote revocation and recovery with evidence a reviewer can follow.

**Current state:** Aligned planning documents and repository checks exist. Lab implementation is **PLANNED**; operational controls are **NOT TESTED**; owner user acceptance testing (UAT) is **PENDING**. No production-impact or compliance claim is made.

## Focused architecture

One Proxmox host runs four VMs: virtual OPNsense, one Windows Server with Active Directory/DNS/Group Policy, one Windows endpoint and one Linux HTTPS application server. Management, Corporate and Restricted are the three zones. Three synthetic standard users, three role groups and a separate privileged administrator support six application access cases and an access-revocation demonstration.

One simple lab certificate authority signs the application certificate. Tailscale alone exposes one named HTTPS resource in a separate lab tailnet. Two or three log sources, five representative events, one investigation, one repeatable PowerShell/Python operation and one measured application restore complete the lab.

The [architecture](docs/architecture/ARCHITECTURE.md) explains flows, capacity and limits, including manual AD-to-application role mapping. [The assignment](docs/assignments/PROJECT-ASSIGNMENT.md) owns ten FWR requirements, the four-week schedule and the single 100-point rubric. [The guide](docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md) groups practical steps into five phases while retaining separate stage A-L approvals.

## Hardware and safety

The owner reports existing hardware and six ordered components. Ordered does not mean delivered, installed or validated. [Hardware status and preparation](docs/architecture/ARCHITECTURE.md#hardware-status-and-preparation) records the distinction. Receipt, inspection, compatibility, current data/service inventory, backups/recovery and exact destructive-change approval precede installation. Additional hardware does not expand scope.

Start offline. No protected home/production trust, identities, credentials, routes, Microsoft 365, PE-DAP, customer data, corporate website testing or hosting integration is permitted. Independently isolated egress needs separate approval. Protected-network checks use configuration/passive review and lab-owned mocks, never probes of real protected systems.

## Editable Lab Deliverable Templates

The [five planned submission filenames](docs/assignments/PROJECT-ASSIGNMENT.md#expected-deliverables) are the approved **T7 target, not yet created**. T7 requires separate approval.

The [eight existing T5 Word/Excel shells](docs/README.md#editable-lab-deliverable-templates) remain unchanged as legacy artifacts of the earlier baseline. Their old counts, IDs and rubric are historical and must not drive current implementation. Keep working records private; publish only reviewed sanitized summaries.

## Testing and evidence

[Ten focused tests](docs/testing/TEST-PLAN.md) connect requirements, architecture, security controls, acceptance and future deliverables. All operational actual/evidence fields are empty. [Acceptance](docs/testing/ACCEPTANCE-CRITERIA.md) requires completed mandatory subchecks and separate owner UAT; critical failures block acceptance regardless of score.

With Python 3.11+ and the existing pinned [documentation environment](docs/governance/DOCUMENTATION-BUILD.md):

```powershell
python scripts/validate_docs.py --require-finalized
python scripts/validate_office_templates.py
python scripts/build_docs.py --check --rebuild-check
python -m unittest discover -s tests -v
git diff --check
```

These checks validate documentation, preservation and bounded publication risks; they do not test lab security. CI remains read-only, commit-pinned, without retained checkout credentials or lab access. Manual content/metadata/history review and rendered PDF inspection remain necessary.

## Project documentation

The [documentation library](docs/README.md) links Markdown sources and generated PDFs. Markdown is authoritative; task reports/addenda are Markdown only and frozen when finalized. Existing report PDFs remain byte-frozen archives.

- [Security controls](docs/security/SECURITY-REQUIREMENTS.md), [decisions](docs/governance/DECISIONS.md) and [risks](docs/governance/RISKS.md) explain safeguards and unresolved gates.
- [T6 report](docs/reports/T6-Report.md) records specification alignment; [T5](docs/reports/T5-Report.md) preserves original template validation.
- [All task reports](docs/reports/INDEX.md) preserve engineering history; [project final report](docs/final-report/FINAL-REPORT.md) remains a template.
- [Glossary](docs/guides/GLOSSARY.md) and [official references](docs/governance/REFERENCES.md) explain terms and proposed commands.

Use focused task branches, reviewed public-safe commits/PRs, exact-head CI and intentional main synchronization under [AGENTS.md](AGENTS.md). No background upload. Licensing and repository-protection settings remain owner decisions.

**Next task:** T7 Office-template migration only, after explicit scope/preservation/validation approval. T6 authorizes no installation, VM/network/directory change, remote enrollment or security-test execution.
