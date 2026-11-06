# Advanced engineering assignment: Enterprise Zero Trust Security Architecture

| Field | Value |
| --- | --- |
| Project ID | HL-CYB-001 |
| Difficulty | Advanced |
| Discipline | Cybersecurity engineering, enterprise architecture, and technical business analysis |
| Current phase | Planning and repository bootstrap; implementation NOT STARTED |
| Assignment baseline | 2026-11-05, owner timezone America/Toronto |
| Assessment model | Evidence-based engineering assessment followed by separate owner UAT |
| Publication | Public, reviewed artifacts in `waqashamdani-ca/enterprise-zero-trust-security` |

## Description and background

Design, build in individually approved future stages, and evaluate an isolated enterprise security lab that demonstrates resource-focused Zero Trust principles. The simulated organization, Purple Eye, has engineering, operations, and administrative staff who need different access to a small set of synthetic business services. Remote working, privileged administration, certificate lifecycle management, and investigation of access decisions must be supported without connecting to production.

Traditional network membership is insufficient proof of authorization. The assignment asks the engineer to combine identity, device controls, scoped network access, application authorization, and usable audit evidence. Explain where the lab approximates an enterprise and where it lacks production features such as resilient identity services, continuous device attestation, hardware-protected CA keys, or a staffed monitoring function. See [NIST SP 800-207](https://csrc.nist.gov/pubs/sp/800/207/final).

## Enterprise scenario and business case

Model three business roles: an analyst who reads synthetic reports, an engineer who maintains a test application, and an administrator who manages infrastructure through a dedicated administrative path. Add an unauthorized synthetic user and a revoked remote user for negative tests. Do not use real employees, customer names, company directories, corporate sign-in, or production business records.

The business value is a repeatable environment for evaluating access restrictions and recovery before considering enterprise designs. Reuse supplied hardware, limit resource consumption, produce reviewable engineering decisions, and show how audit trails support investigations. Demonstrate reduced *allowed reachability* against a documented lab baseline; do not invent breach-reduction percentages, cost savings, availability, or enterprise-wide security claims.

## Purpose, objectives, and learning goals

The project must produce a defensible architecture, an operational lab in later stages, and evidence that its controls meet explicit business requirements. The learner will:

1. Translate role-specific workflows into asset inventories, trust boundaries, measurable controls, and acceptance tests.
2. Engineer isolated virtualization and stateful segmentation without altering home or production networking.
3. Build a separate directory, DNS, endpoint baseline, and PKI with recoverable identity operations.
4. Evaluate identity-aware remote access and show both permitted and denied behavior.
5. Correlate policy decisions, endpoint events, and network events using synthetic activity.
6. Automate selected repeatable operations and prove recoverability and accurate documentation.
7. Communicate tradeoffs, limitations, verified results, and unresolved risks in a public portfolio.

CISSP-aligned learning spans security/risk management, asset security, security architecture, communication/network security, identity/access management, assessment/testing, operations, and software development security. This alignment is an educational interpretation, not certification credit or an endorsed course.

## Measurable technical requirements

All requirements below are **PLANNED**, except documentation/bootstrap elements that are explicitly verified in the Task 001 completion report. The test IDs refer to [TEST-PLAN.md](TEST-PLAN.md); acceptance decisions are in [ACCEPTANCE-CRITERIA.md](ACCEPTANCE-CRITERIA.md).

| ID | Required outcome and measurement | Future evidence / tests | Stage |
| --- | --- | --- | --- |
| R01 | Zero production trust, identity sync, credential reuse, customer data, or lab paths into protected home/production assets; demonstrate configuration review plus mock-boundary denial | Approved topology, route/NAT review, T01, T02 | A–D, K |
| R02 | Inventory verified CPU/virtualization, NICs, disk ownership/free space, and recovery path; initial VM disks at most 248 GiB and guest RAM at most 36 GiB, subject to measured capacity | Sanitized readiness report and capacity ledger, T03 | A, B |
| R03 | Restrict hypervisor/firewall administration to the lab administrative path; named administrator, supported MFA, least privilege, and tested emergency console access | Redacted role/management policy and console check, T04 | B, D |
| R04 | Implement at least six separate lab trust zones; every inter-zone permit has owner, direction, destination, service, and justification; all unmatched traffic denied | Rule inventory and allowed/denied flow evidence, T05, T06 | C, D, H |
| R05 | Separate `ad.lab.test` forest, lab DNS and GPO; at least six synthetic standard users in three role groups plus two separate privileged lab accounts; no external trust | Synthetic object summary, DNS/GPO outputs, T07, T08 | E |
| R06 | At least one supported Windows member endpoint and one supported Linux endpoint; host firewalls enabled, updates recorded, no ordinary-user local administration | Baseline and privilege checks, T09 | F |
| R07 | Offline standalone root and separate online issuing CA; issue a scoped lab TLS certificate; validate trust, expiration, and revoked-certificate rejection in a selected supported relying application | CA design, redacted template review, lifecycle evidence, T10, T11 | G |
| R08 | Role-to-resource matrix with at least twelve explicit allow/deny cases, including same-zone controls; revoke a user's resource access within a measured target of fifteen minutes after policy change | Policy matrix, revocation timing, T06, T12 | H, K |
| R09 | Evaluate Tailscale and Twingate sequentially in separate lab-only environments; scoped identities/devices, MFA, one named resource per pilot, denied-user and revocation tests; no subnet-wide or exit-node exposure | Separate pilot reports and limitation matrix, T13, T14 | I |
| R10 | Collect at least six source classes: firewall, hypervisor, directory, Windows endpoint, Linux endpoint, and remote access; at least 95% of a 20-event synthetic set searchable within five minutes, clock offsets at most two seconds, thirty-day retention design with capacity proof | Ingestion/clock/retention measurements, T15, T16 | J |
| R11 | No secrets, actual internal addresses, sensitive identities, production exports, or proprietary source in public artifacts or published history; every evidence artifact individually reviewed | Automated findings plus manual staged/history review, T00, T17 | All |
| R12 | Two bounded lab automation operations with reviewed targets and rollback; a repeated run makes zero unintended changes; check/diff output reviewed privately | Change summary and repeat-run result, T18 | L |
| R13 | Encrypted, off-compute backup of representative identity/application material; demonstrate a restore with proposed RPO at most 24 hours and RTO at most four hours; document excluded assets and dependency order | Timed isolated recovery and backup-age record, T19 | L |
| R14 | Execute every approved mandatory test; 100% of critical tests pass and at least 95% of applicable noncritical cases pass; no unresolved high-severity issue; owner UAT separately recorded | Traceability and independent observations, T01–T20 | K, L |
| R15 | Complete assignment, stage guide, architecture, threat model, decisions, risks, and report; each claimed achievement references reviewed evidence; all local Markdown links resolve | Repository validation and evidence index, T00, T20 | Task 001, L |
| R16 | Public repository uses `main`, controlled task branches/PRs after bootstrap, read-only documentation CI, reviewed commits, and exact local/remote synchronization | Git/CI verification and PR conventions, T00 | Task 001, all |

## Scope, exclusions, assumptions, and constraints

In scope: design and later approved construction of a virtual-first lab, synthetic enterprise identities/data, controlled DNS/PKI, host and network policies, two separate remote-access pilots, lightweight central logging, bounded automation, and recovery verification.

Out of scope: production deployment, corporate Microsoft 365 integration, PE-DAP code or configuration, production website or hosting changes, AWS Lightsail production resources, real customer records, cross-forest or cloud production federation, public service exposure, offensive testing outside approved synthetic lab targets, licensing selection, high availability, clustering, and certification/compliance claims.

Supplied hardware is a Dell Precision 5820 (Xeon W-2125, 80 GB RAM, 512 GB NVMe), a Lenovo Xeon laptop (119 GB RAM), an HP 410-019 (16 GB RAM, at least 250 GB storage), additional Windows/Linux test laptops, and Google Wifi mesh. These are owner-supplied descriptions, not an inspected inventory. NIC counts, firmware, disk contents, usable capacity, CPU support, OS support, ownership, and backup suitability remain unverified.

Do not assume any planned technology is installed. Work within existing hardware where feasible. Disk capacity and safe physical uplink separation are likely constraints; a single NVMe is not resilient storage. No budget, evaluation-license entitlement, remote-access subscription, or additional hardware purchase is authorized by this assignment.

## Prerequisites and dependencies

Before each stage, obtain owner approval for that stage and resolve its blocking decisions. Required prerequisites include a dedicated lab administrator identity, physical console access, confirmed disk backups before installation, independently recorded recovery instructions, official installation media with integrity verification, evaluation/license terms, a private inventory/secrets store, and an approved isolation/egress topology. The offline baseline does not require a home network change.

The detailed dependency chain is A → B → C → D → E → F → G → H → I → J → K → L. Minimal local logging and backups start with the first installed component; centralized aggregation is finalized in J. Stage I additionally requires approved isolated egress, lab-only external identities, vendor plan verification, and an MFA/recovery plan. If egress cannot be separated safely, keep the pilot pending rather than weaken isolation.

## Expected architecture and trust boundaries

Use the Dell as a proposed single virtualization host, subject to Stage A verification. Separate management, identity/PKI, user endpoints, application services, monitoring, and remote-access connector zones using private virtual bridges with no physical ports. An optional, separately approved egress bridge may connect only the firewall WAN to a dedicated uplink. The default baseline remains disconnected from home and production networking.

Proxmox is the hypervisor management plane. OPNsense enforces inter-zone and egress policies. Active Directory supplies lab identity; host/application authorization remains necessary even when a packet is permitted. A powered-off root CA with no virtual NIC anchors a separate issuing CA. A dedicated administrative path, central event collectors, and scoped remote-access components support control and investigation. See the [architecture and flow matrix](ARCHITECTURE.md).

Map NIST's logical policy engine/administrator/enforcement roles to a combination of documented authorization policy, directory/remote-access administration, firewall/host controls, and application authorization. The lab is a bounded approximation: segmentation or deploying a VPN product alone does not establish full Zero Trust maturity.

## Technologies and implementation alternatives

| Capability | Proposed approach | Alternative and decision condition |
| --- | --- | --- |
| Virtualization | Proxmox VE on verified dedicated hardware | Existing supported Hyper-V or another hypervisor if bare-metal use is not approved; document a design change |
| Boundary enforcement | Virtual OPNsense with isolated bridges | Physical firewall and managed switch in a future approved expansion |
| Directory | Windows Server Evaluation, AD DS, DNS, GPO | An isolated Linux directory may support a comparison but cannot silently replace AD learning outcomes |
| PKI | Offline standalone root and AD CS issuing CA | A simpler lab CA reduces complexity but requires an explicit R07 exception and revised acceptance |
| Remote access | Separate Tailscale and Twingate pilots | Choose one for later operation only after documented comparison; neither connects to corporate tenants |
| Monitoring | Windows Event Collector plus Linux/syslog collection | Add a SIEM only after storage/resource review and approval; it is not installed by this task |
| Automation | PowerShell, Python, Ansible | Use the smallest supported tool for the approved operation; avoid overlapping automation ownership |
| Repository checks | Standard-library Python and GitHub Actions | Add dependencies only for a demonstrated gap with an approved supply-chain review |

These are proposed architecture choices; owner approval and version-specific checks occur at stage entry. Use [official technical references](REFERENCES.md), not unverifiable copied commands.

## Security requirements and threat model

Protect home/production separation, administrative authority, directory credentials, CA keys, synthetic resource integrity, audit trails, and repository publication. Model a compromised ordinary endpoint, stolen lab credentials, a misconfigured connector, an overly broad firewall rule, a malicious or mistaken privileged user, supply-chain changes, and accidental data publication.

For each threat, identify entry point, trust boundary, prevention, detection, safe validation, and residual risk in [SECURITY-REQUIREMENTS.md](SECURITY-REQUIREMENTS.md). Use default deny, separate standard/admin identities, explicit resource authorization, scoped DNS and remote access, private secrets storage, and recovery evidence. No production attacks or real credential collection are permitted.

## Standards alignment

The [tailored control matrix](SECURITY-REQUIREMENTS.md#tailored-control-matrix) links requirement/test IDs to NIST SP 800-207 principles, NIST SP 800-53 Rev. 5 controls (Release 5.2.0 baseline reference), and CIS Controls v8.1. It is a project-authored mapping for learning and review, not an official crosswalk or an assertion of compliance. Consult the current catalogs linked in [REFERENCES.md](REFERENCES.md) before implementation.

## Deliverables and final outcomes

Task 001 delivers a reviewable assignment, architecture, approval-gated A–L guide, requirements, threat/control matrix, test/acceptance plan, decision/risk registers, accurate report, safe repository scaffold, validator/tests, and public GitHub bootstrap where authentication permits.

Later approved stages deliver the isolated lab, sanitized inventories and design diagrams, role/flow matrices, identity/GPO and PKI baselines, two remote-access comparisons, monitoring and detection evidence, two focused automations, a timed recovery report, a requirements-to-test/evidence index, owner UAT records, and a final limitations-aware portfolio report. No live artifacts are implied by these planned outcomes.

## Testing and acceptance

Use predeclared synthetic sources, destinations, identities, and expected outcomes. Positive tests prove required workflows; negative tests prove denied reachability or authorization; security tests evaluate scoped controls; recovery tests prove restoration. Tests that would touch a protected network use lab-owned mock destinations and policy inspection instead. Security tests require separate stage approval.

Each test includes an independent observation and a sanitized evidence record. A failure blocks its critical acceptance gate. Record unexecuted tests as NOT RUN, unsupported functions as an explicit gap, and owner-accepted exceptions with residual risk. See [test procedures](TEST-PLAN.md) and [acceptance gates](ACCEPTANCE-CRITERIA.md). Task 001 acceptance covers documentation/Git only.

## 100-point evaluation rubric

| Assessment area | Points | Evidence required for full credit |
| --- | --- | --- |
| Business analysis and governance | 8 | Clear role workflows, scope, approvals, decisions, and risk ownership |
| Architecture and capacity | 12 | Defensible boundaries, sizing, dependency model, and realistic limitations |
| Isolation and network enforcement | 15 | Reviewed deny-by-default rules, no protected-network path, positive and mock-negative evidence |
| Directory and endpoint identity | 12 | Separate forest, synthetic roles, DNS/GPO, hardened Windows/Linux endpoints |
| PKI and certificate lifecycle | 10 | Offline root, scoped issuing CA, issuance/trust/expiry/revocation demonstration |
| Least privilege and resource authorization | 10 | Twelve role/resource cases, same-zone enforcement, measured revocation |
| Remote-access comparison | 8 | Separate Tailscale/Twingate pilots, MFA, narrow resources, negative/revocation evidence |
| Monitoring and audit analysis | 8 | Six source classes, measured ingestion/clock targets, retention capacity and investigation |
| Validation and recovery | 10 | Traceable critical tests, independent observations, timed isolated restore, separate owner UAT |
| Repeatable automation | 4 | Two reviewed operations with repeat-run evidence and rollback |
| Public portfolio and final reporting | 3 | Sanitized evidence, working documentation/CI, synchronized Git, accurate achievements |

Total: **100 points**. Assess each row as demonstrated, partly demonstrated, or absent against its evidence, with a written score rationale. Planning artifacts alone earn no implementation points. Production integration, secret publication, or an unresolved critical safety test prevents final acceptance regardless of score. An owner-approved scope exception must revise requirements and scoring before evaluation.

## GitHub publication requirements

Use the authorized public repository under `waqashamdani-ca`, default branch `main`, and a supported secure credential store. Check for existing remote work and reconcile it without overwriting or force-pushing. Publish only reviewed project artifacts, using a noreply commit email; no license is selected in Task 001.

Scan the entire proposed file set, staged diff, and history for secrets, actual internal addresses, sensitive identities, images/log metadata, production exports, and proprietary source. Exclude raw evidence and private inventories. Use least-privilege documentation CI; do not connect Actions to the lab. For future work use focused task branches, checks, PR review, and fast-forward synchronization as defined in [AGENTS.md](../AGENTS.md). Confirm remote URL, visibility, default branch, commit equality, clean status, and actual CI outcome.

## Evidence-backed resume achievement objectives

These are future writing patterns, not current achievements:

- "Designed and validated an isolated six-zone security lab" only after linking its reviewed topology, capacity record, and passed boundary tests.
- "Implemented role-scoped access for six synthetic users and separate administrators" only after directory, host, resource, and negative-test evidence exists.
- "Evaluated two identity-aware remote-access approaches" only after separate pilot reports and measured denied/revoked-user behavior.
- "Collected six security event source classes with measured ingestion latency" only after reporting actual sample size, observed percentage, and retained evidence.
- "Demonstrated recovery within a measured RTO" only after a timed restore, stated recovery scope, and verified service behavior.

State exact observed measurements and lab scope, cite evidence IDs, and disclose limitations. Do not claim production impact, CISSP certification, compliance, penetration-test outcomes, or unavailable implementation results.

## Authoritative references

Use the maintained [reference catalog](REFERENCES.md) for NIST, CIS, Proxmox, OPNsense, Microsoft, IETF, Tailscale, Twingate, Ansible, systemd, and GitHub. References were researched for the bootstrap on 2026-11-05; recheck current versions, licensing, security advisories, and exact syntax before a future stage is approved.
