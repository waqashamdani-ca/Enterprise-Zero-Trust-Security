# Lab implementation guide: proposed stages A–L

**DESIGN BLUEPRINT ONLY. No implementation stage has started.** Task 001 creates this guide and the repository; it does not authorize running these procedures. The owner must explicitly approve each stage separately. Stage A is the recommended next task, pending review and approval.

## How to execute a future approved stage

Before work, record its scope, approval reference/date, operator, hardware/software versions, private target inventory, proposed changes, expected outcomes, tests, stop conditions, and rollback. Recheck current vendor instructions and compatibility. Use a clean task branch, update the design first, perform only the approved stage, collect private evidence, publish reviewed synthetic summaries, and request separate owner UAT. Completing a stage does not authorize the next one.

All commands below are **proposed, not executed**. They illustrate verified vendor syntax, not a turnkey deployment script. Run only on the named lab target after stage approval and local help/version checks. Variables such as `$LabDnsAddress` and `$LabCertificatePath` must be populated privately with reviewed lab-only values. Do not paste secrets or real addresses into the repository. GUI labels can change; use the version-specific official documentation in [REFERENCES.md](REFERENCES.md).

Stop a stage if a disk/asset is uncertain, protected connectivity appears, a rollback path is missing, secrets enter output, validation fails, or the approved boundary would be exceeded. Disconnect the approved lab uplink using the console procedure if isolation is in doubt. Preserve private evidence and record the problem. Never "temporarily" bridge the lab to home/production to solve a dependency.

## Stage A — Hardware and virtualization readiness

### Prerequisites

Owner approval for a read-only readiness assessment, access to the supplied devices, an agreed inventory/evidence location outside Git, and confirmation of who owns each device and disk. No reboot, firmware change, software installation, or security testing is included in a read-only approval.

### Procedures

1. Inventory the Dell, Lenovo, HP, and candidate administrator/test laptops. Confirm actual CPU, RAM, storage/free capacity, disk contents, supported operating systems, NIC count/type, power/cooling, and physical console availability. Keep serial numbers and actual addressing private.
2. Inspect virtualization/SLAT support and firmware settings using existing tools; record uncertainty without changing firmware. Identify any existing hypervisor, encryption/recovery dependency, or irreplaceable data.
3. Review the proposed [capacity budget](ARCHITECTURE.md#initial-capacity-budget), reserve/free-space requirements, and CPU contention. Verify a backup location with adequate usable space; the supplied HP is a candidate, not a proven backup target.
4. Draw a private cable/interface map. Identify a lab-only administrator station and offline management segment. Review other adapters, Wi-Fi, VPNs, sharing, and forwarding that could bridge protected networks.
5. Propose the exact disk for a future Proxmox installation, its data-preservation plan, supported boot mode, media verification method, and recovery procedure. Identify the unresolved egress boundary and any hardware dependency.
6. Publish only a sanitized readiness summary, capacity ledger, risks, and go/no-go recommendation. Request separate approval for Stage B; do not reboot into an installer.

### Proposed commands

On each approved Windows lab candidate, local read-only PowerShell; command output stays private until reviewed:

```powershell
Get-CimInstance -ClassName Win32_ComputerSystem
Get-CimInstance -ClassName Win32_Processor
Get-NetIPConfiguration -All
```

Syntax references: [Microsoft inventory and network commands](REFERENCES.md#readiness-and-network-commands). Use existing firmware/storage UI for details not covered by these commands. Do not install an inspection tool during Stage A without expanded approval.

### Expected outcome

A verified asset/capacity inventory, exact disk decision proposal, feasible offline topology, known backup/console recovery path, and explicitly unresolved prerequisites.

### Verification

T03: compare inventory output with physical labels/firmware and storage UI without changing settings. Reconcile supplied versus observed capacity and check that the private topology shows no protected-network connection. This is not a network probe.

### Rollback

Read-only assessment requires no configuration rollback. Close tools, retain private records, and correct any inaccurate public summary through a reviewed commit. Any requested hardware/firmware change becomes a separate approval item.

### Completion criteria

R01/R02 prerequisites are documented; hardware uncertainties and blocking decisions have owners; Stage A engineering review and owner acceptance are recorded separately. No installation is claimed.

## Stage B — Proxmox installation and baseline hardening

### Prerequisites

Accepted Stage A; explicit Stage B approval covering exact host/disk and destructive installation; verified backups and recovery media; physical console; supported hardware; official media and matching vendor-published checksum/signature; private administrator credentials and MFA recovery plan. Offline media/update transfer must not introduce production data.

### Procedures

1. Reconfirm the approved disk immediately before installation. Disconnect unrelated disks where feasible under approval. Stop if labels, capacities, or data differ from the approved record.
2. Boot verified Proxmox media from console. Select only the approved storage and a filesystem appropriate for a single disk; do not claim redundancy or create a cluster. Configure the lab-only management interface and private DNS/time plan.
3. Connect management only to the dedicated offline administrator segment. Do not attach ordinary guests or home uplinks to the management bridge. Keep console access open during access-policy changes.
4. Use a named lab administrator and appropriate scoped roles; configure supported MFA and a protected console/break-glass recovery method. Limit root use to necessary recovery/setup; do not publish recovery secrets.
5. Review supported update repositories/subscription terms. Apply only approved supported updates using verified offline transfer or a separately approved isolated path; record deferred updates as risk. Never disable integrity checks or use unreviewed install scripts.
6. Apply host management restrictions for the actual Proxmox firewall backend/version. Preserve a specific administrator allow rule, deny other management sources, and verify effective policy. Do not switch firewall backends blindly.
7. Record storage/free-space quotas, backup target proposal, local logging/time baseline, and host configuration recovery instructions. Do not create enterprise guests yet.

### Proposed commands

No installation or firewall command is supplied as an executable shortcut. Use the verified media installer and version-matched [Proxmox documentation](REFERENCES.md#proxmox). Inspect installed versions and effective configuration through the supported local UI/CLI help after installation; record exact commands in that stage's reviewed change record.

### Expected outcome

A recoverable single lab hypervisor with an isolated management plane, scoped administrator/MFA, supported patch status, and an accurately measured capacity ledger.

### Verification

T03/T04: inspect installed version, management bindings, roles, firewall state, free storage, and local logs; independently log in using the named administrator and confirm physical console recovery. Use lab-owned mock/unprivileged contexts for denied management checks only if Stage B approval covers them.

### Rollback

Use console to restore the approved prior host/network configuration if access is lost. Reinstallation is destructive and needs approval unless explicitly covered in the Stage B rollback authorization. Restore preinstallation data from the verified backup when applicable; do not overwrite another device to recover the host.

### Completion criteria

R02/R03 baseline evidence, console recovery, supported-version record, private backup location, and owner acceptance exist. No VM, directory, or remote-access implementation is implied.

## Stage C — Virtual enterprise networking and isolation

### Prerequisites

Accepted Stage B, explicit Stage C approval, private nonoverlapping address plan, bridge/interface map, console rollback, and approved management access. All uplinks remain disconnected unless separately approved.

### Procedures

1. Confirm `vmbr0` is management only and its physical port reaches only the dedicated lab administrator segment. Check that the administrator station cannot forward via Wi-Fi/another NIC.
2. Create internal bridges `vmbr10`–`vmbr50` for identity, endpoints, services, monitoring, and remote access. Give them no physical ports and no hypervisor address. Leave bridge names/roles in public docs; keep actual addressing private.
3. Document per-zone gateway and future firewall vNIC mapping. Disable unintended host routing/forwarding between zones; the planned firewall is the only router. Keep offline-root networking absent.
4. Review IPv6 forwarding, RA/DHCPv6, overlay interfaces, host NAT/bridging, and any inherited defaults. Disable routed IPv6 exposure for the baseline while preserving required local OS behavior.
5. If an egress interface is proposed, create it disconnected. Verify that it is not connected to the home LAN and cannot bypass the independent protected-network boundary. Resolve DEC-03 before enabling it.
6. Save a private before/after map and host network backup. Do not start a general guest with a management or uplink adapter to test convenience connectivity.

### Proposed commands

Use the version-matched Proxmox networking UI and inspect its effective bridge/port/address definitions. No host networking command is prescribed until the inspected NIC names and supported network backend are known. See [Proxmox networking](REFERENCES.md#proxmox).

### Expected outcome

Six separately defined trust zones with no physical access from workload bridges and no automatic home/production path. Routing is still absent until the approved firewall stage.

### Verification

T01/T03: inspect the effective bridge membership and private cable map; compare them with the VM attachment plan and physical console view. Review routes/forwarding and IPv6 settings without probing home or production. After test guests are authorized in D/F, repeat isolation observations using lab mocks.

### Rollback

Restore the saved network configuration from physical console, preserving management connectivity. Remove only newly created unused bridges if explicitly covered by rollback approval; never delete an attached interface or reset the host networking wholesale.

### Completion criteria

R01/R04 topology is reviewed, console rollback is viable, no actual addresses appear in Git, and owner acceptance is recorded. A configured bridge alone is not evidence of end-to-end enforcement.

## Stage D — Virtual OPNsense firewall

### Prerequisites

Accepted Stage C, explicit Stage D approval, verified official OPNsense media, approved VM budget and exact vNIC-to-zone map, private rule/alias plan, console access, and disconnected WAN. Online egress remains blocked on DEC-03.

### Procedures

1. Create only the firewall VM within the proposed budget. Attach management and internal interfaces according to the bridge map. Add WAN disconnected; verify vNIC identifiers rather than guessing interface order.
2. Install from verified media at console. Assign interfaces, private addresses, and explicit gateway/routing behavior. Do not run DHCP on the management/home network or give guests a second default gateway.
3. Replace installer permissive LAN rules with the [flow matrix](ARCHITECTURE.md#inter-zone-policy-matrix). Add narrow required infrastructure permits and explicit protected-destination denies ahead of approved egress rules; finish with logged default deny.
4. Audit management listeners, anti-lockout rules, floating/group rules, automatic rules, NAT, existing states, IPv6, UPnP/NAT-PMP, and firewall-originated traffic. Keep a specific management allow path and console recovery before narrowing access. NAT never substitutes for a deny policy.
5. Add private aliases for protected destinations and named allowed services. Review DNS alias refresh/shared-hosting limitations. Do not publish the real alias members. Default external egress is denied, and no inbound forwarding is configured.
6. Do not blindly toggle "Block private networks" on WAN: behavior depends on the approved uplink. If a private transit source is required, document the exact exception and independent protection before changing it. No exception permits home access.
7. Enable local administrative/rule logging and save an encrypted private firewall backup outside Git. Connect an approved isolated uplink only after the owner approves its concrete topology and rollback. Otherwise leave Internet/remote-access dependencies pending.

### Proposed commands

Use the supported OPNsense console/UI. No direct packet-filter disabling or blanket rule command is proposed. Review current [virtual installation, rules, and interface documentation](REFERENCES.md#opnsense) before configuration.

### Expected outcome

A stateful, default-deny lab router/firewall with explicit service exceptions, protected-network exclusions, controlled management, logging, and recovery configuration.

### Verification

T01/T02/T04/T05/T06: review effective rules, routes, aliases, listeners, states, and vNIC attachments. Using only approved lab mock endpoints, confirm a permitted flow and a denied flow on each relevant boundary and observe corresponding rule counters/logs. Never test protected real targets. Clear only the scoped lab test states under approval when validating a policy change.

### Rollback

Disconnect WAN first if isolation is uncertain. Use console to restore the last approved private configuration; do not disable the entire filter to regain access. Verify protected-network denial before reconnecting any approved uplink.

### Completion criteria

R01/R03/R04 evidence passes for the implemented offline scope; any online dependency is explicitly pending. No broad LAN-allow, exposed administrator service, or unauthorized protected path remains. Owner UAT and Stage E authorization are separate.

## Stage E — Windows Server Evaluation, AD, DNS, and GPO

### Prerequisites

Accepted Stage D, explicit Stage E approval, official supported Windows Server Evaluation media/terms, approved identity VM, private DNS/address/time plan, separate lab passwords and DSRM custody, and supported identity backup/recovery design. Verify current evaluation activation/expiry requirements; no corporate tenant or product key is used.

### Procedures

1. Create the DC VM on the identity bridge only, with approved CPU/RAM/disk, static private addressing, and a lab-only hostname. Patch through the approved path and record edition/build and evaluation deadlines.
2. Confirm DNS/time are consistent and no corporate suffix, resolver, trust, cloud registration, or identity sync is configured. Plan activation through approved egress if required; if no safe path exists, stop rather than attach the VM to home.
3. Install AD DS/DNS and create a new `ad.lab.test` forest. Keep DSRM and administrator secrets in the private store. Do not create a DNS delegation into production or select a functional level without version compatibility review.
4. Create OUs for users, privileged identities, servers, endpoints, and service accounts; three role groups; six synthetic standard users; and two separate privileged lab accounts. Apply delegated group-based rights instead of routine Domain Admin use.
5. Configure lab forward/reverse DNS and the domain time hierarchy. Limit DNS recursion/forwarding to approved sources and upstreams. Domain members will use lab DNS only; avoid routing internal names to external resolvers.
6. Define GPO baselines for password/lockout, audit policy, host firewall, privileged logon restrictions, and endpoint administration. Pilot in a test OU, review precedence/resultant policy, and expand only after approved checks. Avoid lockout tests that threaten the only recovery administrator.
7. Establish supported system-state backup and document isolated directory recovery. A VM snapshot is not the directory backup strategy. Do not join corporate devices or enable hybrid/cloud integration.

### Proposed commands

On the new approved **lab DC only**, elevated PowerShell. These commands change the server and the second can reboot it; execute only under Stage E approval after prerequisite checks:

```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
Install-ADDSForest -DomainName 'ad.lab.test' -InstallDNS
```

Allow the supported interactive secure DSRM prompt; never embed a password. Syntax: [Microsoft AD deployment](REFERENCES.md#active-directory-dns-and-policy). Exact parameter choices/functional levels require the selected server version's help. No command is executed by Task 001.

### Expected outcome

A separate synthetic directory/DNS domain, delegated role model, pilot GPO baseline, private credential recovery, and supported backup procedure.

### Verification

T07/T08: check directory/DNS health and synthetic records; independently resolve a known service and inspect resultant GPO on the later approved member endpoint. Review trusted domains, DNS forwarders, cloud registration, group membership, and account counts without touching production. Record expiry/activation limitations.

### Rollback

Revert only the new pilot GPO/group change using documented backups; do not demote/delete a DC casually. Recover an unusable new forest only within the approved isolated rebuild/system-state procedure. Stop and obtain further approval if recovery would affect another asset or overwrite evidence.

### Completion criteria

R05 is demonstrated in the approved scope, production independence is verified by configuration review, recovery custody exists, and owner acceptance is recorded. Endpoints are not assumed joined until F.

## Stage F — Linux and Windows endpoints

### Prerequisites

Accepted Stage E, explicit Stage F approval, supported/licensed Windows and Linux media, endpoint VM budgets, private inventory, lab DNS/time, reviewed host firewall baseline, and clean rollback images/backups.

### Procedures

1. Create a Windows member VM and Linux VM on the endpoint bridge with one NIC each. Use synthetic device names. Do not migrate a real user profile, corporate endpoint, browser session, or credential store.
2. Patch and establish named standard users plus separate administration. Join only the approved Windows VM to `ad.lab.test`; Linux directory join is optional and requires a separate design decision rather than assumed parity.
3. Apply Windows pilot GPO and a scoped Linux baseline. Keep host firewalls enabled, unnecessary services disabled, and inbound management restricted to the approved administrative path.
4. Set lab DNS/time and review network profiles, IPv6 behavior, shared folders/clipboard/media, guest integration, forwarding, and adapters for bypass paths. Export no raw system inventory publicly.
5. Add the minimal synthetic application/service in its separate service VM if included in Stage F approval. Protect it with application roles rather than assuming that a firewall allow authorizes all data.
6. Retain local logs, approved backups, and a private baseline record. Capture sanitized baseline differences and unresolved OS/driver constraints.

### Proposed commands

On the approved Windows **member endpoint**, not the DC, read-only PowerShell:

```powershell
Test-ComputerSecureChannel -Verbose
```

This [Microsoft command](REFERENCES.md#endpoint-and-certificate-verification) checks the member's domain secure channel; do not use it as a DC health verdict. Review OS firewall/privilege state through supported tools for each installed version; do not prescribe unverified Linux distribution commands before choosing a distribution.

### Expected outcome

Two isolated, supported, baseline-managed endpoints and a minimal protected synthetic service, with standard-user workflows and separate administrative identities.

### Verification

T08/T09/T12: inspect resultant policy and local privileges, then independently sign in as a standard synthetic user and exercise one authorized and one unauthorized resource. Confirm one-NIC attachment and active host firewalls; use lab mocks for denied management access.

### Rollback

Revert the specific pilot policy or restore the clean endpoint baseline. Rebuilding a lab endpoint is allowed only if its destructive rollback was approved and evidence/data are preserved. Do not alter domain-wide policy to work around one endpoint failure.

### Completion criteria

R06 and applicable R05/R08 checks pass with separate engineering and owner acceptance. A Linux endpoint without directory join is labeled accurately.

## Stage G — Enterprise PKI and identity security

### Prerequisites

Accepted Stage F, explicit Stage G approval, approved CA design and algorithms/lifetimes, root/issuing VM budgets, supported AD CS media/roles, secure private key/backup custody, reviewed certificate templates, transfer media, and internal CRL/AIA publication plan. Root and issuing CA must be separate from the DC.

### Procedures

1. Create a standalone offline root VM with **no virtual NIC**. Configure its CA identity, key protection, certificate lifetime, renewal schedule, and backup ceremony using supported AD CS procedures. Power it down except for controlled signing/renewal work.
2. Create the separate domain-joined issuing CA in the identity zone. Generate its request and transfer only the reviewed request/certificate/CRL artifacts through approved media; never move the root private key to the issuer.
3. Configure internal AIA/CDP locations and publish the required chain and CRLs with a renewal/calendar owner before issuing leaf certificates. Availability of those endpoints must not require Internet or production DNS.
4. Restrict CA administration and certificate-template enrollment to named lab roles. Avoid unrestricted subject/SAN supply, unnecessary authentication EKUs, broad enrollment, and private-key export. Record template review and separation-of-duties limits in a one-owner lab.
5. Distribute lab trust only to approved lab systems. Issue a short-lived synthetic TLS server certificate for the selected application, bind it, and verify hostname, chain, usage, validity, and private-key protection.
6. Revoke a dedicated test certificate, publish a new CRL, account for caches, and verify failure in a selected relying application configured to check revocation. Test a separate expired/untrusted certificate without changing the domain clock. Record clients that soft-fail or do not check revocation.
7. Create encrypted supported CA backups and document isolated restoration, key custody, CRL renewal deadlines, and compromise response. No private key, certificate export, or root trust is placed in home/production or Git.

### Proposed commands

On an approved lab verification endpoint, with `$LabCertificatePath` pointing to the reviewed synthetic public certificate:

```powershell
certutil -verify -urlfetch $LabCertificatePath
```

This [Microsoft verification command](REFERENCES.md#endpoint-and-certificate-verification) can contact AIA/CDP URLs carried by the certificate. Inspect those URLs first and permit only lab destinations. It supplements, and cannot replace, an end-to-end relying-application test.

### Expected outcome

A two-tier isolated PKI with offline root, constrained issuance, internal trust/revocation services, lifecycle evidence, and recoverable private key custody.

### Verification

T10/T11: inspect offline-root NIC absence and issuing-template permissions; independently test valid, untrusted/expired, and revoked certificates in the selected lab application. Record cache/soft-fail behavior and CRL validity, without manufacturing a pass from a certificate dump alone.

### Rollback

Remove only the pilot binding/trust from the approved lab systems and restore the previous service certificate. Revoke affected test certificates. CA deletion/rekey or private-key recovery needs explicit scope approval; never restore an old CA snapshot and assume revocation/database consistency.

### Completion criteria

R07 passes with issuance and relying-application rejection evidence, backups, renewal owner, and explicit limitations. Universal revocation enforcement or production-grade HSM security is not claimed.

## Stage H — Least privilege and Zero Trust policies

### Prerequisites

Accepted Stage G, explicit Stage H approval, role/resource inventory, named policy owners, approved twelve-case matrix, lab-only test identities, host/application enforcement capability, and policy backups.

### Procedures

1. Translate analyst, engineer, administrator, unauthorized, and revoked-user workflows into exact resources, actions, ports, identity groups, and available device/context conditions.
2. Create at least twelve allow/deny cases covering each role and resource, same-zone paths, direct-IP/name paths, ordinary-user management denial, and revoked access. Include the administrative path and infrastructure exceptions.
3. Apply narrow group/resource authorization and service accounts, then matching network/host restrictions. Remove redundant broad permits only after confirming required dependencies and console recovery.
4. Check additive group memberships, inherited application rights, cached sessions, direct endpoint routes, overlay adapters, local administrators, and service credentials for alternative access paths.
5. Revoke a dedicated synthetic user's access; measure from the approved policy change to observed resource denial, including existing sessions and new sessions. Define cache/session invalidation and the fifteen-minute target explicitly.
6. Document which decisions are identity-aware and which are static network rules. Record unavailable device posture or continuous reevaluation as gaps; do not equate segmentation with full Zero Trust.

### Proposed commands

No reusable live access policy or command is supplied before the resource/application choice. Export reviewed synthetic policy summaries and use vendor-native effective-permission tools under Stage H approval. Keep actual user/tenant/address values private.

### Expected outcome

A traceable identity/resource policy set with twelve cases, independent same-zone controls, and a measured access-revocation path.

### Verification

T06/T12: execute each approved case in its named identity/device context, observe the application result and independent firewall/host/application audit event, and compare effective permissions. Record revocation timing and limitations of existing-session termination.

### Rollback

Restore the specific previous policy from private backup via the protected administrator path. Revert only approved test memberships; never re-enable broad domain/network permissions to recover access. Recheck isolation after any rollback.

### Completion criteria

R08 passes all twelve declared cases and the revocation target, or a documented gap blocks acceptance. Separate owner UAT confirms business workflows remain usable.

## Stage I — Lab-only Tailscale and Twingate pilots

### Prerequisites

Accepted Stage H, explicit Stage I approval for both sequential pilots, resolved isolated-egress decision, current vendor plan/terms review, independent lab-only identities/tenants, MFA and account recovery, connector/device budgets, and approved pilot resource/ports. No corporate SSO, tailnet, Twingate network, or production-connected client is permitted.

### Procedures

1. Verify that the proposed external identity cannot automatically enroll in an existing corporate environment. Create/confirm separate lab administration, test-user groups, recovery, audit visibility, and any posture/logging feature availability before enrollment.
2. Pilot Tailscale first. Replace its initial allow-all policy with reviewed explicit narrow grants/ACLs before enrolling devices. Verify the effective policy rather than assuming omitted or empty policy content denies access. Restrict tag owners and eliminate every additive wildcard path.
3. Expose one synthetic resource through a scoped dedicated lab component or explicitly approved directly enrolled lab endpoint. No subnet router, exit node, route advertisement, public sharing, or production DNS integration. For direct enrollment, treat overlay host policy as a separate boundary because it can bypass OPNsense.
4. Review outbound vendor connectivity and local DNS changes, authorize only necessary destinations/protocols, and test permitted, unauthorized, and revoked identities plus offline/recovery behavior. Record plan-specific limits rather than claiming unsupported device posture/MFA coverage.
5. Disable/disconnect the first pilot and restore the approved DNS/routes before starting Twingate. Do not run competing client interceptors simultaneously.
6. Create a separate Twingate lab network and connector in the remote zone using the currently supported vendor deployment method. Keep deployment tokens in the supported private secret mechanism. Define one exact Resource and explicit port restrictions; do not leave all-port/wildcard defaults.
7. Independently restrict connector-to-resource reachability in OPNsense/host policy, allowing only needed DNS and application dependencies. A connector compromise must not gain directory, management, or protected-network access. No inbound Internet listener/port forward is added.
8. Repeat the same role/deny/revocation cases, capture permitted vendor audit data privately, and compare identity/device requirements, policy precision, DNS behavior, logging, revocation timing, limitations, and recovery. Revoke unused pilot tokens/devices and close temporary egress permits.

### Proposed commands

On the enrolled **lab Tailscale device** only, read-only status after policy review:

```text
tailscale status
```

See [Tailscale documentation](REFERENCES.md#tailscale) and [Twingate documentation](REFERENCES.md#twingate). Status output can identify users/devices/addresses and is private. No token-bearing enrollment command, remote shell installer, or deployment credential is included in this guide. Verify current vendor endpoint/port requirements at execution time; do not open blanket Internet egress from all guests.

### Expected outcome

Two comparable, isolated, resource-scoped remote-access pilot reports without a production connection, subnet exposure, or persistent broad policy.

### Verification

T13/T14: independently inspect effective vendor policies and local routes/DNS, then test the same allowed/denied/revoked cases against the one lab resource. Inspect connector-zone enforcement and provider logs. Use lab mock protected targets for any attempted bypass case; never test actual home/production destinations.

### Rollback

Disable the pilot resource, revoke pilot enrollments/tokens, stop the connector/client, restore approved lab DNS/routes, and remove temporary egress permits under the approved rollback. Confirm console administration still works. Do not delete a vendor account or existing environment unless expressly authorized.

### Completion criteria

R09 and applicable R08/R10 tests pass for both pilots with measured limits; plan or egress blockers remain explicit if unresolved. Owner chooses whether either pilot should remain enabled in a future task.

## Stage J — Security monitoring and audit logging

### Prerequisites

Accepted Stage I or an explicitly approved dependency exception, explicit Stage J approval, available storage/collector VM budget, lab PKI/DNS/time, six-source event inventory, retention/access policy, private evidence location, and approved synthetic event-generation scope.

### Procedures

1. Confirm local logging from every existing component. Inventory firewall, hypervisor, DC/DNS, Windows endpoint, Linux endpoint, and remote-access audit sources; document provider export/retention constraints and gaps.
2. Create the WEC and Linux/syslog collectors in the monitoring zone. Restrict administration and source submission. Configure source-initiated Windows event forwarding with an explicit source-computer ACL and authenticated transport; use TLS where designed. Do not broadly enable remote management.
3. Configure encrypted/authenticated syslog or supported secure collection for firewall, hypervisor, and Linux events. If a source lacks the selected transport, document an approved isolated-path exception and residual risk; do not claim encryption that is absent.
4. Select security-relevant events: synthetic authentication failures/success, privilege/group changes, administrative actions, DNS/policy changes, certificate events, allowed/denied flows, and remote-session decisions. Avoid passwords, tokens, message bodies, or customer data.
5. Normalize UTC timestamps and check each source against the chosen lab time authority. Set source-health/missing-log alerts and restrict log deletion/export. Keep raw logs private.
6. Generate twenty approved benign synthetic events across all six classes, capture local and collector timestamps, measure search latency, and document dropped/duplicated records. At least nineteen must be searchable within five minutes; every class must be represented.
7. Measure daily ingestion/storage rate and calculate thirty-day retention plus margin within the capacity ledger. Configure rotation/quota and alert thresholds. A calculation proves design capacity only; demonstrate actual aging/rotation separately and label the observation period.

### Proposed commands

On the approved Linux collector or source, local read-only journal inspection:

```text
journalctl --since today --no-pager
```

Use the [systemd journal reference](REFERENCES.md#logging-and-automation) matching the installed distribution. Output is private. WEC setup is performed using the reviewed [Microsoft subscription guidance](REFERENCES.md#logging-and-automation), not an unrestricted remote-management shortcut.

### Expected outcome

Six-class collection with access controls, UTC correlation, measured ingestion, retention sizing, and a documented response to a missing source.

### Verification

T15/T16: compare local source events with collector search results and record independent wall-clock/timing observations. Check denied log access and source interruption using only an approved lab source. Verify retention settings and capacity calculations separately from actual elapsed retention.

### Rollback

Disable only the new subscriptions/forwarders, restore previous source policy, and retain local logging and captured evidence. Do not clear event logs to fix collection or reset a collector containing needed records.

### Completion criteria

R10 meets the six-source, 19-of-20 latency, clock, and retention-design targets with explicit export/transport limitations. No claim of thirty days of observed retention is made before that interval exists.

## Stage K — Functional, negative, and security validation

### Prerequisites

Accepted prior stages or recorded scope exceptions, explicit Stage K authorization identifying synthetic sources/targets and permitted tests, current backups, test windows/stop conditions, the frozen role/flow matrix, and no protected assets in target inventory.

### Procedures

1. Review [TEST-PLAN.md](TEST-PLAN.md), requirement coverage, installed versions, target list, and expected results. Resolve tests that would touch protected systems by using configuration inspection and lab-owned mocks instead.
2. Execute required functional workflows for DNS/domain logon/GPO, endpoints, application roles, PKI, and each remote pilot. Do not infer success from a running service or a green vendor dashboard.
3. Execute explicit deny cases for inter-zone, same-zone, ordinary-user management, wrong resource/port, untrusted certificate, and revoked identity. Use bounded connection checks; no broad scan, exploit, brute-force test, or malware is authorized by this guide.
4. Correlate each observed result with effective policy and independent logs/counters. Check alternative adapters/routes, IPv6, DNS bypass, cached sessions, and overlay enforcement using scoped lab cases.
5. Run approved certificate-revocation, policy-revocation, logging interruption, and scoped isolation/fail-closed checks without changing home networking or probing production. Stop immediately on unexpected reachability.
6. Record pass/fail/blocked/NOT RUN, evidence IDs, defects/severity, residual risk, retest scope, and independent observation. Fixes require a bounded approved change; do not alter the expected result merely to pass.
7. Submit engineering results for review, then run separately documented owner UAT for business usability. Do not mark owner acceptance from engineering self-review.

### Proposed commands

No general scanning or attack command is proposed. Version-verified bounded checks must be written into the approved test record with exact lab-only destination, rate, expected response, and stop condition before execution. The repository validator may be run locally but cannot verify operational controls.

### Expected outcome

A traceable, evidence-backed evaluation with honest failures/gaps, independent observations, and separate owner UAT.

### Verification

T01–T17/T20 as applicable: all critical tests pass, at least 95% of approved applicable noncritical cases pass, and no high-severity unresolved issue remains. Read results against the frozen matrix and inspect evidence/actual test coverage; skipped cases do not count as passed.

### Rollback

End the bounded tests, disable temporary test accounts/policies under approval, restore affected approved configurations, and verify isolation. Preserve original failure evidence. Any destructive recovery or policy expansion beyond approval requires a new owner decision.

### Completion criteria

R14 has an engineering verdict and separate UAT state. Unexecuted tests and accepted exceptions are explicit; critical failures block final implementation acceptance.

## Stage L — Automation, recovery, and final documentation

### Prerequisites

Accepted Stage K, explicit Stage L approval, two named automation operations/targets, reviewed credentials mechanism, off-compute encrypted backup storage, supported AD/CA recovery procedures, isolated restore network, approved recovery scope/RPO/RTO, and final-report template.

### Procedures

1. Select two small useful operations, such as a lab inventory summary and one reviewed baseline-policy deployment. Document target allowlists, expected changes, credential handling, logging, failure behavior, and rollback before code. Do not automate production or secret publication.
2. Implement using the smallest suitable PowerShell/Python/Ansible tool. Review installed module versions and dependencies before any approved installation. Add focused tests for boundary/target rejection and meaningful failure paths.
3. For configuration automation, inspect syntax/check results privately, execute on one approved lab target, compare actual desired state through a separate tool, and repeat. Record zero unintended changes on the second run; a no-op check alone is not proof of idempotence.
4. Configure encrypted off-compute backups with private key custody and verify backup freshness. Include supported directory system-state/CA artifacts for the chosen recovery scope, not just VM snapshots. State excluded assets and a retention/capacity plan.
5. Restore the approved representative identity/application scope into disconnected networks. Follow the [dependency order](ARCHITECTURE.md#monitoring-recovery-and-residual-limits), prevent duplicate live DC identity, and use supported AD/PKI restore guidance. Measure backup age and full service recovery time against RPO 24 hours/RTO four hours.
6. Validate restored DNS/authentication, certificate/revocation publication, authorization, logs, and data consistency. Restore encrypted backup/key access as part of the drill. Do not reconnect until isolation/policy checks pass.
7. Complete the requirements/test/evidence index, final limitations and risks, architecture-as-built differences, operating/recovery instructions, remote-pilot comparison, rubric assessment, and evidence-backed achievement statements. Leave owner UAT separate and explicit.
8. Run local repository checks, manually review every proposed public artifact and history, publish on the task branch, verify CI, and use a PR for review. Synchronize local `main` only after reviewed merge. Stop after the approved scope.

### Proposed commands

For a **future, existing, reviewed** Ansible playbook, on the approved lab control node only:

```text
ansible-playbook baseline.yml --syntax-check
ansible-playbook baseline.yml --check --diff --limit lab-pilot
```

`baseline.yml` and `lab-pilot` do not exist in Task 001. [Ansible documentation](REFERENCES.md#logging-and-automation) explains that check mode is a simulation; modules can lack support and tasks can override it. Review the playbook before connecting. Diff output may expose secrets, so disable sensitive diffs and keep output private. Neither command authorizes a normal deployment.

Local repository checks, already permitted for Task 001 and later document changes:

```powershell
python scripts/validate_docs.py
python -m unittest discover -s tests -v
git diff --check
```

### Expected outcome

Two bounded repeatable automations, a timed isolated restore, an accurate final implementation report, sanitized evidence, and reviewed Git synchronization.

### Verification

T18/T19/T20: independently inspect actual state after automation, measure recovery with a separate clock/service observation, validate backed-up data against the approved synthetic baseline, and review the final requirement/evidence index. Confirm UAT with the owner; no self-awarded acceptance.

### Rollback

Restore the specific configuration backup for an automation failure. Keep restored systems isolated and return to the last known approved lab baseline. Do not overwrite the only valid backup, bring duplicate DCs online, or destroy restore evidence. Cleanup/destructive rebuild needs explicit authorization.

### Completion criteria

R12–R15 pass for the approved scope; actual measurements and residual limitations are recorded; public artifacts pass review/CI; owner UAT and final acceptance are explicit. A final implementation completion claim is prohibited until these conditions are met.

## Task 001 stop

This document is a blueprint. After repository bootstrap and synchronization verification, stop for owner review. Do not begin Stage A, install Proxmox, create VMs, deploy AD/PKI, configure OPNsense, enroll remote access, or generate security-test traffic without the corresponding new authorization.
