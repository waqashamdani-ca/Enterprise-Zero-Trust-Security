# Lab Implementation Guide

<a id="before-beginning-the-lab"></a>
<a id="how-to-use-this-manual"></a>

## How to use the guide

The analyst reads reports. The engineer reads maintenance instructions. The unassigned user is denied. Follow the [assignment](../assignments/PROJECT-ASSIGNMENT.md) for required outcomes.

Follow the five phases in order: [infrastructure](#phase-1-prepared-infrastructure), [identity and endpoints](#phase-2-identity-and-endpoint-security), [access controls](#phase-3-zero-trust-access-controls), [monitoring and recovery](#phase-4-monitoring-automation-and-recovery), then [validation and submission](#phase-5-validation-and-final-submission). Read each procedure first. Obtain approval before each stage A-L, covering assets, changes, validation and rollback. Use the [architecture](../architecture/ARCHITECTURE.md) and [technical reference](reference/01-Prepared-Infrastructure.md) for detail.

Use private copies of the [five Office files](#required-lab-deliverables), numbered **01-05**. Record observations, dates and private evidence references in the named sections. Use synthetic users and separate lab passwords; keep raw evidence private. Leave unperformed checks **NOT TESTED**. If a result differs, stop the affected work, follow its recovery plan and log it in **Deliverable 04 > Issue Log**.

<a id="phase-1-infrastructure-and-network"></a>

## Phase 1: Prepared Infrastructure

Verify the Dell Precision 5820 with Proxmox, HP desktop with physical OPNsense, TP-Link TL-SG108E switch and GL.iNet Beryl AX upstream router.

**Before you start:** Have read-only stage A approval, the private network map and backup/recovery record, and Dell/HP console access. Missing map, version or recovery details mean stop. Changes need separate B (host), C (network) or D (firewall) approval; this phase installs nothing.

<a id="step-1---inspect-what-is-actually-available"></a>
<a id="step-2---protect-windows-prove-recovery-and-approve-the-target"></a>
<a id="step-3---install-proxmox-and-open-its-management-page"></a>

### A. Verify the lab equipment and VM resources

**WHERE**

Dedicated lab administrator computer; Dell and HP consoles. Use private management addresses.

**STEPS**

1. Sign in at both consoles. Compare device identities and cables with the private map. Confirm the original Windows disk, data and services remain protected and their recovery record is available.
2. Open **Proxmox > Dell node > Summary**, then storage > **Summary**. Compare CPU, memory and usable storage with the [capacity budget and reserves](../architecture/ARCHITECTURE.md#initial-capacity-budget).
3. Select **DC1**, **WIN1** and **APP1 > Hardware** in turn. Compare processors, memory and disk allocations with that budget. Physical OPNsense on HP is outside these guest totals.
4. Compare the GUI inventory with device labels and the private physical/firmware record. Record a difference before continuing.

**CHECK**

Exactly three workload VMs; allocations total 6 vCPU / 16 GiB RAM / 160 GiB disks. Measured capacity also covers host, free-space and temporary-restore reserves. Both consoles and recovery records are available.

**RECORD**

**Deliverable 01 > Hardware & Readiness**, **Virtual Machines** and **Resource Allocation**. Enter observations and evidence references.

<a id="step-4---create-the-three-network-bridges"></a>
<a id="step-5---install-opnsense-and-identify-its-interfaces"></a>

### B. Verify network zones and management access

**WHERE**

Administrator computer: Proxmox, HP OPNsense and switch web pages.

**STEPS**

1. Open **OPNsense > Interfaces > Assignments**. Match Management, Corporate and Restricted to the HP ports and private map.
2. Open **Proxmox > Dell node > System > Network**. Compare bridge ports, addresses and VLAN-aware settings with the [approved relationships](reference/01-Prepared-Infrastructure.md#physical-map-and-proxmox-bridges).
3. Open each VM's **Hardware > Network Device**. Match bridge and VLAN tag to the map: DC1/WIN1 in Corporate; APP1 in Restricted, with one zone NIC each.
4. Open the switch's **VLAN > 802.1Q VLAN** and **802.1Q PVID Setting** pages. Compare tagged/untagged membership and port defaults with the map; change nothing.
5. Inspect the [management restrictions](reference/01-Prepared-Infrastructure.md#management-access): named administrator sources/services, effective host/device rules, supported multifactor authentication and console recovery.

**CHECK**

Three zones reach HP; no switch/host route bypasses OPNsense. Workload bridges have no host address. Only the dedicated path reaches management; APP1's approved overlay is the sole extra interface.

**RECORD**

**Deliverable 01 > Network Zones** and **Allowed Network Flows**.

<a id="step-6---enter-the-allowed-connections-and-check-isolation"></a>

### C. Verify isolation and required network access

**WHERE**

Administrator computer: read-only Windows, Beryl AX and firewall/host views.

**STEPS**

1. Open Windows **Settings > Network & internet > Advanced network settings**. Compare adapters with the isolation record; flag extra Wi-Fi, VPN or shared connections.
2. In Beryl AX **INTERNET**, inspect **Ethernet**, **Repeater**, **Tethering** and **Cellular**. Keep upstream disconnected until independent isolation and egress are approved.
3. Compare [FF-01 through FF-08](../architecture/ARCHITECTURE.md#inter-zone-policy-matrix) with effective firewall/host rules, states, NAT and listeners. Use the [flow checklist](reference/01-Prepared-Infrastructure.md#default-deny-and-allowed-flows); unlisted access stays denied.
4. Complete the [IPv4/IPv6, route and trust checks](reference/01-Prepared-Infrastructure.md#isolation-and-routing). GUI inspection alone does not prove home/production isolation.
5. For separately approved active validation, use [lab-owned mocks](reference/01-Prepared-Infrastructure.md#approved-active-checks). Record allowed and denied behavior plus policy/log evidence under FWT-01/FWT-02. Never probe home or production.

**CHECK**

Map/flows match. FWR-01/FWR-02 need FWT-01/FWT-02 evidence and second observations. Unperformed active checks stay **NOT TESTED**.

**RECORD**

**Deliverable 01 > Allowed Network Flows** and **Deliverable 03 > Test Cases**.

**Before Phase 2:** Resolve mismatches; carry pending checks forward. For unexpected connectivity, stop and use [console isolation/recovery](reference/01-Prepared-Infrastructure.md#console-recovery-and-rollback).

## Phase 2: Identity and Endpoint Security

DC1 manages lab Windows accounts; WIN1 uses them; APP1 has a protected Linux baseline. Coverage: FWR-03/FWR-04 and FWT-03/FWT-04.

**Before you start:** Approvals: E for directory work, F for endpoint settings; missing workload creation also needs the applicable host/network approval. Have the private identity/network plan, approved media, versions, policy values and console recovery. Keep lab DNS, time, credentials and identities separate from home/production; create no trust or identity synchronization.

<a id="step-7---create-and-install-the-three-workload-vms"></a>

### A. Verify or create the three workload VMs

**WHERE**

**Proxmox > Dell node**, then each guest's **Hardware** and **Console**.

**STEPS**

1. Find **DC1**, **WIN1**, **APP1**. Verify existing guests; create a missing guest only with approval and the [guest profiles](reference/02-Windows-Directory-and-Policy.md#vm-profiles-and-installation). Protect the original Windows disk/services.
2. Check CPU / RAM / disk: **DC1 2 / 6 GiB / 64 GiB; WIN1 2 / 6 GiB / 64 GiB; APP1 2 / 4 GiB / 32 GiB**; retain host/recovery reserves.
3. In **Hardware > Network Device**, match the private bridge/tag/MAC map: one zone NIC each; Corporate for DC1/WIN1, Restricted for APP1. Management stays separate; physical OPNsense is on HP.
4. Open **Console**. Verify name, supported OS/build, approved media, private recovery and lawful offline update/activation. Windows 11 needs supported CPU, UEFI/Secure Boot and TPM 2.0; no bypass.

**CHECK**

Three workload VMs; own virtual disks; totals 6 vCPU / 16 GiB / 160 GiB. Resolve a mismatch through approved console recovery.

**RECORD**

**Deliverable 01 > Virtual Machines / Resource Allocation**; **02 > Implementation Overview**. Include update/activation gaps.

<a id="step-8---give-dc1-its-lab-address-and-install-active-directory"></a>

### B. Configure DC1 and Active Directory

**WHERE**

DC1 console, approved administrator: **Server Manager**. Active Directory (AD) manages Windows users.

**STEPS**

1. Open **Local Server > Ethernet > adapter Properties > Internet Protocol Version 4 > Properties**. Set approved Corporate address/mask/gateway and **DC1 as DNS**, without external alternates. Check name/MAC/time.
2. Verify an existing directory; otherwise use **Manage > Add Roles and Features > Role-based or feature-based installation > DC1 > Active Directory Domain Services**. Include tools; install.
3. For a new forest only: notification flag > **Promote this server to a domain controller > Add a new forest**. Enter **ad.lab.test**, retain DNS and approved functional levels; store the DSRM recovery credential privately.
4. Review [prerequisites and paths](reference/02-Windows-Directory-and-Policy.md#ad-ds-and-dns), resolve warnings, install and restart.
5. Open **Tools > DNS > DC1 > Forward Lookup Zones > ad.lab.test**. Check host/service records and [forest/controller health](reference/02-Windows-Directory-and-Policy.md#directory-verification), including SYSVOL/NETLOGON.

**CHECK**

Forest/controller/DNS work. Role installation alone is insufficient. On failure inspect DNS/time/prerequisites; use [supported directory recovery](reference/02-Windows-Directory-and-Policy.md#recovery-and-version-notes).

**RECORD**

**Deliverable 02 > Active Directory and User Roles**; **03 > Test Cases**, FWT-03.01-.03.

<a id="step-9---create-the-users-groups-and-dns-record"></a>
<a id="step-10---join-win1-and-check-windows-logon"></a>

### C. Create lab users and groups, then join WIN1

**WHERE**

DC1 **Server Manager > Tools > Active Directory Users and Computers**; WIN1 console.

**STEPS**

1. In **ad.lab.test**, verify or create the approved organizational units (OUs) or containers for users, groups, privileged identities and member computers. Keep DC1 in **Domain Controllers**; do not assume **Users** is the approved folder.
2. In the user folder select **New > User**. Create missing **ava**, **eli**, **uma**, with unique private passwords and approved first-logon choices. Verify the separate named administrator in its privileged folder.
3. Select **New > Group** in the group folder: **Global**, **Security**. Create/verify **LabReaders**, **LabMaintainers**, **LabAdmins**. In **Properties > Members > Add**, use **Check Names**: Readers = ava/eli; Maintainers = eli; Admins = separate administrator only.
4. Inspect each user's **Member Of** and each group's **Members**. Keep uma outside both application-related groups and all three standard users outside privileged groups. [Assign only approved administrator rights](reference/02-Windows-Directory-and-Policy.md#users-groups-and-permissions); group names grant none.
5. Open DC1 **Tools > DNS > Forward Lookup Zones > ad.lab.test > New Host (A or AAAA)**. Add/verify **app**, IPv4 A record, with APP1's approved private address.
6. On WIN1 set its approved Corporate address/gateway and DC1-only DNS. Open **System Properties > Computer Name > Change > Domain**, enter **ad.lab.test**, use the prompted join credential and restart. Move WIN1 to the approved computer OU on DC1.
7. Sign in on WIN1 as **ava@ad.lab.test**. Verify lab DNS, domain membership and policy using the [join checks](reference/02-Windows-Directory-and-Policy.md#win1-domain-join-and-verification). Test eli/uma logon within approval.

**CHECK**

Three standard users, three role groups and one separate privileged administrator; memberships and standard logon agree. AD groups do not assign Apache roles. On failure, inspect DNS/time/membership and correct only the approved object; never elevate a standard user.

**RECORD**

**Deliverable 02 > Active Directory and User Roles**; **03 > Test Cases**, FWT-03.01-.03. Later application roles use distinct passwords; six access cases and revocation remain required.

<a id="step-11---apply-essential-windows-policy-and-host-rules"></a>

### D. Apply Windows security policies

**WHERE**

DC1 **Server Manager > Tools > Group Policy Management**; DC1/WIN1 security consoles.

**STEPS**

1. Link the account-policy Group Policy Object (GPO) at **Domains > ad.lab.test**. Enter [approved password/lockout values](reference/02-Windows-Directory-and-Policy.md#account-and-endpoint-policy).
2. Link WIN1's endpoint GPO to its computer OU: Microsoft Defender enabled; all Windows firewall profiles **On**, inbound **Block**; reviewed exceptions only.
3. Apply WIN1 logon auditing and a separate DC1 GPO at **Domain Controllers**, using the [exact auditing paths](reference/02-Windows-Directory-and-Policy.md#auditing-and-effective-policy).
4. In **Windows Defender Firewall with Advanced Security > Inbound Rules**, scope [AD/DNS/time rules](reference/02-Windows-Directory-and-Policy.md#scoped-service-ports). Remove approved broad overlaps; FF-02 needs same-zone host enforcement.
5. Inspect winning policy, protection and updates on both targets. Check WIN1 **Administrators**; run the [standard-user denial/admin control](reference/02-Windows-Directory-and-Policy.md#privilege-and-protection-checks).

**CHECK**

Settings and privileges match approval; policy/log evidence supports behavior. On failure restore changed pilot settings at console; keep protections enabled.

**RECORD**

**Deliverable 02 > Windows and Linux Endpoint Controls**; **03 > Test Cases**, FWT-03/FWT-04.

<a id="step-12---configure-app1-networking-and-its-host-firewall"></a>

### E. Configure APP1 networking and host protection

**WHERE**

APP1 Proxmox **Console**, approved sudo administrator. APP1 stays outside AD.

**STEPS**

1. Match interface MAC with **Hardware > Network Device** and the private map. Inspect [addresses/routes/DNS/rules](reference/03-Linux-Network-and-Host-Policy.md#interface-and-backend-inspection); save recovery copies.
2. If needed, edit [Netplan](reference/03-Linux-Network-and-Host-Policy.md#netplan-configuration-and-rollback): approved private interface/address/gateway, DC1-only DNS. Check syntax, use the timed trial and verify rollback.
3. Verify [lab-only time](reference/03-Linux-Network-and-Host-Policy.md#lab-only-time), without public/corporate DNS/time fallback or another backend.
4. Apply [nftables policy](reference/03-Linux-Network-and-Host-Policy.md#nftables-policy): default-deny input/forward, exact WIN1/admin HTTPS, IPv4/IPv6 restrictions; future overlay on APP1 alone.
5. Use [initial load or scoped atomic replacement](reference/03-Linux-Network-and-Host-Policy.md#initial-load-and-persistence). Preserve other tables. Verify [rules/routes/services/reboot persistence](reference/03-Linux-Network-and-Host-Policy.md#verification-and-console-recovery); test HTTPS permit/deny when its listener exists.

**CHECK**

Configuration/state agree; forwarding is off. On failure restore saved files at console. Never flush all rules or add another firewall manager.

**RECORD**

**Deliverable 02 > Windows and Linux Endpoint Controls**; **03 > Test Cases**, FWT-04. Include second observations.

**Before Phase 3:** Compare directory/logon/DNS/policy/privilege evidence. Unperformed FWT-03/FWT-04 checks, including later app cases, stay **NOT TESTED**. Resolve failures through approved console recovery; directory rebuild/snapshot rollback needs separate supported recovery approval.

## Phase 3: Zero Trust Access Controls

Let approved users reach the right HTTPS page, then prove that removed permissions stop working. Coverage: FWR-03/05/06 and FWT-03/FWT-05/FWT-06.

**Before you start:** Approvals: G for certificates/trust, H for Apache, I for remote access; E also covers AD revocation. Have private versions/network/identity records, saved configurations and console recovery. External access needs independently isolated, approved egress. Use the linked references; missing scope means stop.

<a id="step-13---create-the-offline-ca-and-app1-request"></a>
<a id="step-14---sign-the-certificate-and-prepare-browser-trust"></a>

### A. Create and verify HTTPS certificates

**WHERE**

Approved existing offline signing workstation: terminal; APP1 Proxmox **Console**; WIN1 lab browser.

**STEPS**

1. On the offline signer, create the [encrypted CA key and 365-day public root](reference/04-HTTPS-and-Application-Roles.md#offline-ca-and-private-key-custody) in a new private directory. Keep the key offline and passphrase in recovery custody; add no CA VM/service.
2. On APP1 create its [private server key and certificate signing request](reference/04-HTTPS-and-Application-Roles.md#app1-key-and-certificate-request). Transfer only the request to the signer.
3. On the signer, [sign one 90-day leaf](reference/04-HTTPS-and-Application-Roles.md#leaf-signing-and-verification) for **app.ad.lab.test**. Verify subject alternative name (SAN), serverAuth, chain/constraints, dates and remaining validity; leave domain time unchanged.
4. [Transfer public certificates](reference/04-HTTPS-and-Application-Roles.md#public-certificate-transfer-and-browser-trust) to APP1; keep its key root-only. After B starts HTTPS, record WIN1's untrusted rejection, then import only the fingerprint-checked public root into its approved lab store and retry. Never bypass warnings.

**CHECK**

Correct chain/name/dates; untrusted rejection then normal trusted HTTPS. No home/production trust changes. On failure stop and use [certificate recovery](reference/04-HTTPS-and-Application-Roles.md#recovery-and-version-notes).

**RECORD**

**Deliverable 02 > HTTPS Certificate Configuration**; **03 > Test Cases**, FWT-05: public properties, custody/scope, browser evidence. **02 > Implementation Results and Limitations**: certificate-revocation services excluded.

<a id="step-15---create-the-two-pages-and-separate-app-accounts"></a>
<a id="step-16---enable-https-and-run-the-six-application-cases"></a>

### B. Configure the Apache application and accounts

**WHERE**

APP1 Proxmox **Console**, approved sudo administrator and root editor; WIN1 browser.

**STEPS**

1. Save settings. Use approved Apache 2.4/password-utility packages/media; [create synthetic pages](reference/04-HTTPS-and-Application-Roles.md#synthetic-pages-and-application-accounts) at **/reports/** and **/maintenance/**.
2. Create/verify separate test accounts **ava**, **eli**, **uma**, with distinct application passwords. Create the password file once; never overwrite it to add a user.
3. Set manually assigned roles in **/etc/labapp/groups**: **LabReaders: ava eli**; **LabMaintainers: eli**; uma neither. AD provides Windows logon: no application single sign-on or automatic synchronization, no fourth app administrator.
4. Apply [HTTPS/group configuration](reference/04-HTTPS-and-Application-Roles.md#apache-https-and-group-authorization); require each page's group. Disable HTTP/reviewed default sites; syntax-check before restarting.
5. Verify Apache active, **TCP 443 only**, protected key/password/group files, no extra service. Complete A's trust sequence; preserve FF-03 firewall/host restrictions.

**CHECK**

HTTPS/group checks work. On failure inspect DNS/TLS/files and [restore saved settings](reference/04-HTTPS-and-Application-Roles.md#recovery-and-version-notes). Never use a generic authenticated-user allow.

**RECORD**

**Deliverable 02 > Application Accounts and Permissions**; **03 > Test Cases**, FWT-03.10/FWT-05: versions, effective files, roles and evidence. Exclude passwords/hashes.

### C. Test the six application access cases

**WHERE**

WIN1 **Browser > Developer tools > Network**; APP1 console: Apache logs.

**STEPS**

1. Use a fresh browser context per user and valid application credentials. Close all private windows between users.
2. Disable cache; reload each exact path. Confirm the actual server request/status using the [evidence method](reference/04-HTTPS-and-Application-Roles.md#certificate-browser-test-and-six-case-evidence).
3. Compare all six requests with Apache logs/effective groups; keep eli's working maintenance context for D.

| Case | Account | Page | Expected HTTP result |
| --- | --- | --- | --- |
| C01 | ava | /reports/ | ALLOW / 200 |
| C02 | ava | /maintenance/ | DENY / authenticated 403 |
| C03 | eli | /reports/ | ALLOW / 200 |
| C04 | eli | /maintenance/ | ALLOW / 200 |
| C05 | uma | /reports/ | DENY / authenticated 403 |
| C06 | uma | /maintenance/ | DENY / authenticated 403 |

**CHECK**

A failed login/401 or unreachable service is not role denial. On failure preserve evidence; inspect account/group/inherited rules.

**RECORD**

**Deliverable 03 > Test Cases**, FWT-03.04-.09; link from **02 > Six Application Access Tests**. FWT-03.01-.03 and mapping/revocation .10-.13 remain mandatory.

<a id="step-17---remove-an-application-permission-and-prove-it-is-gone"></a>

### D. Revoke an application permission

**WHERE**

APP1 root editor; DC1 **AD Users and Computers**; WIN1 browser.

**STEPS**

1. Confirm eli's maintenance access; save groups and change time against a separate observer clock.
2. In **/etc/labapp/groups**, remove eli from **LabMaintainers**, keeping **LabReaders: ava eli** and [ownership/mode](reference/04-HTTPS-and-Application-Roles.md#application-permission-revocation).
3. Under E approval remove eli on DC1: approved **LabMaintainers > Properties > Members**. Record both changes; AD membership does not update Apache.
4. Disable cache; force a **/maintenance/** server request in eli's existing authenticated browser, then a fresh context with valid app credentials. Compare both with Apache logs/effective groups; check reader access.

**CHECK**

Both maintenance requests return authenticated 403; reader permission stays. On failure inspect files/cache/inheritance. Restore permissions only with recorded explicit test/recovery approval.

**RECORD**

**Deliverable 03 > Test Cases**, FWT-03.10-.13; **02 > Access Revocation**. Record changes, request/denial times, observed elapsed time and cache/state treatment; no revocation-time SLA.

<a id="step-18---enroll-lab-only-tailscale-with-a-narrow-policy"></a>
<a id="step-19---test-and-revoke-remote-access"></a>

### E. Configure, test and revoke Tailscale access

**WHERE**

Separate lab **Tailscale admin console > Access controls / Machines**; APP1 console; one approved existing Windows remote client.

**STEPS**

1. Verify [independent isolation, identities, MFA and recovery](reference/05-Tailscale-Policy.md#independent-isolation-and-identity-prerequisites) before external egress. The client must have no direct zone route to APP1. Missing prerequisites leave FWT-06 **NOT TESTED**.
2. Save the lab policy; apply the [explicit deny-all baseline](reference/05-Tailscale-Policy.md#explicit-deny-all-baseline) before enrollment. Inspect every additive grant/ACL, SSH rule and tag owner; a blank policy is insufficient.
3. [Enroll APP1 and the existing client](reference/05-Tailscale-Policy.md#device-enrollment) with separate approved lab identities. Inspect device records. Keep subnet routes, exit node, Tailscale SSH, Funnel, Serve and public sharing off; use no home/production identity or trust.
4. Apply the [exact client-to-APP1 TCP 443 grant](reference/05-Tailscale-Policy.md#exact-https-only-grant); review enrolled addresses privately. [Map app.ad.lab.test to APP1's overlay address](reference/05-Tailscale-Policy.md#overlay-name-mapping-and-host-enforcement), approve only lab-root trust, and verify independent APP1 host rules/forwarding. FF-06 adds no DC1, WIN1, Proxmox or OPNsense access.
5. [Test approved HTTPS, unauthorized identity and wrong listening port/resource](reference/05-Tailscale-Policy.md#allowed-and-denied-remote-tests). Use working positive controls and vendor/device/host/Apache evidence. A closed port or broken DNS is insufficient. The [Phase 5 mock dependency](#step-24---prepare-the-permitted-and-denied-network-checks) needs separate scope; do not broaden grants.
6. Restore the approved context through its authorized sequence; confirm working HTTPS. Record time, then [remove the client grant and exact device authorization](reference/05-Tailscale-Policy.md#client-and-grant-revocation), keeping APP1 intact.
7. Force new server requests in the existing browser and a fresh context. Both must fail; compare policy/device/log state, observed denial time and cache/connection-state treatment. Re-enrollment or permission restoration needs approval.

**CHECK**

Only approved APP1 HTTPS works; unauthorized/wrong-port and both revoked contexts deny. OPNsense alone cannot prove overlay enforcement. On failure stop remote access and use [deny-all/device recovery](reference/05-Tailscale-Policy.md#recovery-and-version-notes).

**RECORD**

**Deliverable 03 > Test Cases**, every FWT-06 subcheck; **02 > Tailscale Remote Access / Access Revocation**. Include evidence, actual elapsed time and final device/policy state; keep identities/addresses/raw logs private.

**Before Phase 4:** Compare all mandatory FWT-03/FWT-05/FWT-06 subchecks with second observations; missing work stays **NOT TESTED**. Log failures in **04 > Issue Log**. Recover saved app/policy files, lab-only trust and exact remote authorization within approval; preserve key custody and failed evidence.


## Phase 4: Monitoring, Automation and Recovery

Explain five security events, repeat one useful local operation and demonstrate APP1 recovery. Coverage: FWR-07/08/09 and FWT-07/FWT-08/FWT-09. Use existing logs and the three workload VMs; HP runs physical OPNsense.

**Before you start:** J approval covers logs/events; explicit L portions cover automation and recovery. Existing D/H/I/K scopes must cover any mock check; E/H/I cover any final permission changes. Keep raw evidence private. Recovery is **BLOCKED** until the [encrypted backend and private isolation plan](reference/07-Backup-and-Recovery.md#required-private-recovery-plan) are approved; no safe port/bridge mapping is supplied here.

<a id="step-20---open-the-logs-and-produce-five-benign-events"></a>

### A. Collect five security events

**WHERE**

DC1 **Event Viewer**; physical HP **OPNsense** web interface; APP1 Proxmox **Console**; WIN1 sign-in/browser.

**STEPS**

1. Verify DC1's [Kerberos success/failure auditing](reference/06-Logs-Automation-and-Test-Tools.md#dc1-security-log-and-auditing), approved log-reader rights and selected account's lockout margin.
2. Open **Windows Logs > Security**, **Firewall > Log Files > Live View**, and APP1's [Apache logs](reference/06-Logs-Automation-and-Test-Tools.md#apache-logs-and-bounded-reads). Check access, retention/rotation and source clocks.
3. Reuse current matching evidence or perform each [approved benign action](reference/06-Logs-Automation-and-Test-Tools.md#five-benign-event-procedures) once. No additional traffic merely to fill a worksheet.

| Event | Action and matching source |
| --- | --- |
| E01 Directory authentication success | Valid online WIN1 logon; DC1 Security success |
| E02 Directory authentication failure | One wrong-password attempt, then stop; DC1 Security failure |
| E03 Application access allowed | ava opens /reports/ with valid app credentials; Apache allow |
| E04 Application access denied | ava opens /maintenance/ with valid app credentials; Apache role denial |
| E05 Firewall access denied | One approved request to a known-listening lab target; matching OPNsense block |

4. Locate each event by identity, resource, source/destination, service and time. Compare the actual [firewall rule](reference/06-Logs-Automation-and-Test-Tools.md#opnsense-live-view-and-effective-policy) or app group; a failed connection alone proves no control.
5. [Compare source/observer UTC](reference/06-Logs-Automation-and-Test-Tools.md#source-and-observer-time-comparison), record their difference and link each private original. Five distinct categories are required.

**CHECK**

Five attributable records agree with actions and policy. On failure inspect auditing, time filters, logging and listener state; never repeat password guesses, clear logs or disable lockout.

**RECORD**

**Deliverable 03 > Security Events**, E01-E05; **Evidence Index**; **Test Cases**, FWT-07.01-.07/.09. Include actuals, private evidence, versions, operator/date and second observations.

<a id="step-21---explain-one-denied-access-event"></a>

### B. Investigate one denied-access event

**WHERE**

Deliverable 03; WIN1 request view; APP1 or physical HP policy/log view.

**STEPS**

1. Choose E04 or E05. Record who requested which resource/service, client context, source/destination, actual time and outcome.
2. [Compare the matching log and effective rule/group](reference/06-Logs-Automation-and-Test-Tools.md#denied-access-investigation); identify the intended enforcing control.
3. Link one working allowed control to that listening service and a second observation. Distinguish correct policy denial from incorrect credentials, broken DNS, stopped service or network failure.
4. Record conclusion, limitations and evidence references. Preserve failures and link any correction/retest in **Deliverable 04 > Issue Log**.

**CHECK**

The request, intended policy and observed decision agree. If evidence is missing, leave the conclusion unverified; do not infer enforcement from a timeout or change the expectation.

**RECORD**

**Deliverable 03 > Denied Access Investigation**; link the event, **Evidence Index** and **Test Cases**, FWT-07.08/.09.

<a id="step-22---run-the-one-capacity-summary-automation"></a>

### C. Run the capacity-summary automation

**WHERE**

WIN1 local **Windows PowerShell**, standard user; an approved existing private directory outside Git.

**STEPS**

1. Review and save the [complete capacity script](reference/06-Logs-Automation-and-Test-Tools.md#complete-win1-capacity-script) privately. Preserve its WIN1/ad.lab.test target and path guards; use existing policy/signing, without bypass.
2. Inspect output-directory permissions, reparse points and the existing summary. Capture before-state; only **WIN1-capacity.json** may be replaced.
3. [Run once](reference/06-Logs-Automation-and-Test-Tools.md#successful-and-repeated-execution). Compare DeviceID/Size/FreeSpace with **File Explorer > This PC > drive Properties**, using consistent byte units.
4. Run successfully a second time. Compare before/after files and settings; other files, accounts, network and system settings must remain unchanged.
5. Run the [safe invalid-target check](reference/06-Logs-Automation-and-Test-Tools.md#invalid-target-rejection) using only a disposable private copy with its expected hostname changed; retain the real script and verify no summary write.
6. Run the real script's [invalid-output-path check](reference/06-Logs-Automation-and-Test-Tools.md#invalid-output-path-rejection). Verify rejection and unchanged summary independently after each negative check.

**CHECK**

One local fixed-disk query, two successful runs, both safe rejections and separate OS/state observations. On failure stop; correct only approved paths/rights. Do not elevate or widen writes to force success.

**RECORD**

**Deliverable 03 > Automation Verification**, A01-A07; **Test Cases**, FWT-08.01-.07; **Evidence Index**. Keep the script/output and failure evidence outside Git.

<a id="step-23---back-up-app1-and-restore-it-in-isolation"></a>

### D. Back up APP1 and restore it in isolation

**WHERE**

Dell **Proxmox**; original/restored APP1 **Console**; WIN1 browser; physical HP **OPNsense**; approved encrypted external storage.

**STEPS**

1. Clear the [private recovery prerequisites](reference/07-Backup-and-Recovery.md#required-private-recovery-plan): exact encrypted backend, separate recovery key, unused temporary ID, space, cleanup and existing isolated path through physical HP. Missing design means **BLOCKED / NOT TESTED**; do not begin the drill.
2. Decide the [final application/remote authorization state](reference/07-Backup-and-Recovery.md#final-authorization-state) under E/H/I scope before backup. Record approved changes/retests; retain revoked state if restoration is unapproved.
3. Create and separately protect the [APP1 file manifest](reference/07-Backup-and-Recovery.md#app1-manifest-and-private-custody). [Verify external encryption/mount/storage and mountpoint guard](reference/07-Backup-and-Recovery.md#external-mount-and-backup-storage); a host directory or snapshot is insufficient.
4. Cleanly shut down original APP1; confirm **Stopped**. [Back it up once](reference/07-Backup-and-Recovery.md#backup-archive-and-original-off-sequence), inspect archive identity/time/disk coverage and protect the sole archive. Keep the original off throughout restore testing.
5. Start a separate observer clock immediately before confirming [Restore to the unused temporary ID](reference/07-Backup-and-Recovery.md#restore-a-disconnected-copy). Keep start/live restore off; before console boot disconnect every restored NIC and disable automatic startup. Never overwrite original APP1 or the sole backup.
6. At the disconnected copy's console, [stop and disable copied Tailscale](reference/07-Backup-and-Recovery.md#copied-tailscale-and-integrity-check). Verify inactive/disabled state and all manifest hashes/content before temporary changes; preserve mismatches.
7. Verify the [approved physical-firewall isolation checklist](reference/07-Backup-and-Recovery.md#physical-firewall-isolated-test-path) before attaching any restored NIC. Keep home/production and duplicate identities disconnected. Use only named temporary client/firewall changes; no new bridge/VLAN/NIC/port mapping or firewall bypass.
8. Through that isolated WIN1 path, [test trusted HTTPS](reference/07-Backup-and-Recovery.md#https-role-checks-and-recovery-time): ava /reports/ allows; ava /maintenance/ denies with valid credentials. Compare Apache/group evidence. Stop the observer clock only after integrity and usable application checks; record actual elapsed time.
9. [Disconnect and shut down the copy, then clean up](reference/07-Backup-and-Recovery.md#cleanup-rollback-and-off-compute-custody). Restore saved client/rule settings before original startup; verify original HTTPS/roles/approved remote state. Safely lock/detach the encrypted backup into separate custody, with its recovery key stored separately.

**CHECK**

Backup/restore output, separate clock, file integrity and HTTPS allow/deny agree. On failure leave the copy disconnected, preserve original/sole backup and follow approved recovery; never reconnect broadly or invent a recovery time/PASS.

**RECORD**

**Deliverable 03 > Backup & Restore**, B01-B10; **Test Cases**, FWT-09.01-.10; **Evidence Index**. Record backup age/time, final state, failures and AD/CA/host/physical-firewall recovery exclusions; issues in **04 > Issue Log**.

**Before Phase 5:** All FWT-07/08/09 mandatory subchecks and second observations remain required. Missing or blocked evidence stays **NOT TESTED**. Retain private source logs, output and backup; recover only approved changes. Engineering results and owner acceptance are separate.

## Phase 5: Validation and Final Submission

Verify the ten tests, complete the five submissions and record the owner's decision. Confirm stage K validation and the remaining stage L closeout approval. Reuse earlier evidence only if it covers the current configuration and every applicable check.

<a id="step-24---prepare-the-permitted-and-denied-network-checks"></a>

### A. Prepare and verify network tests

**WHERE**

Approved lab clients and APP1 console. On the administrator computer open **HP OPNsense > Firewall > Log Files > Live View**.

**STEPS**

1. Confirm the applicable D/F/H/I and K scopes for the requests and any temporary changes. Record approval/date, lab source, identity, target, one port, expected policy, observer, stop condition and rollback. Use [Reference 06 > Deferred Phase 5 mock and connection tools](reference/06-Logs-Automation-and-Test-Tools.md#deferred-phase-5-mock-and-connection-tools).
2. Establish working allowed controls. WIN1 reaches APP1 HTTPS, and the dedicated administrator reaches the named management services. Confirm each target is listening before attempting its deny case.
3. For **FWT-01**, use APP1 as the lab-only protected-boundary mock. Use Reference 06's exact logged block and compare its rule hit. Verify independent home/production isolation separately by inspecting cables, adapters, IPv4/IPv6 routes, egress and trust. Keep test traffic on lab-owned targets.
4. For **FWT-02**, use DC1 to APP1 TCP 443 for unlisted inter-zone denial and WIN1 to Proxmox TCP 8006 for ordinary-user management denial. Require a network policy block before login.
5. For **FWT-06**, verify approved remote HTTPS and the dedicated administrator's TCP access to the approved temporary APP1 listener. Use that known-listening wrong port for the remote denial. Keep the Tailscale grant limited to TCP 443 and host/firewall permissions within the approved scope.
6. Make one bounded request per approved case. Match source, destination, port and time to the effective policy and its log or counter. For the overlay, compare Tailscale grants and device state with APP1 host rules and counters. Identify which control actually enforced the denial.
7. Remove only the named temporary block, alias, permits and listener as described in Reference 06. Compare restored settings with the saved baseline, confirm the mock port is closed and recheck normal HTTPS, management and isolation.

**CHECK**

Each denial has a working allowed control and matching policy evidence. A timeout, stopped listener, broken DNS or failed login alone leaves the denial unverified. Record an unattributed denial as NOT TESTED. On failure stop and use the approved console rollback.

**RECORD**

**Deliverable 03 > Test Cases**, FWT-01/02/06 and **Evidence Index**. Link controls, request outcomes, second observations and cleanup. Cross-reference **01 > Allowed Network Flows** and log issues in **04 > Issue Log**.

<a id="step-25---execute-and-record-the-ten-tests"></a>
<a id="historical-requirement-and-test-transition"></a>

### B. Complete the ten formal tests

**WHERE**

**Deliverable 03 > Test Cases** and the [Test Plan](../testing/TEST-PLAN.md).

**STEPS**

1. Filter **Test ID**. Read its **OVERALL** row, every numbered child and the matching Test Plan entry. Complete all 91 mandatory subchecks.
2. Confirm approval, scope and a safe target. For FWT-02 verify one Dell Proxmox host, one separate physical HP OPNsense firewall and exactly three workload VMs (DC1, WIN1 and APP1). Cite the [Architecture](../architecture/ARCHITECTURE.md#physical-and-virtual-topology) and [capacity budget](../architecture/ARCHITECTURE.md#initial-capacity-budget) in the expected result.
3. Execute only approved actions. Record expected and actual results, operator/date/version, private evidence references and second observations. Preserve failures and link each approved correction and retest in **04 > Issue Log**.
4. Use **PASS** for verified results with all mandatory evidence, **FAIL** for executed mismatches, and **NOT TESTED** for blocked, unperformed or unverified checks. **NOT APPLICABLE** never waives a mandatory check. **OVERALL** passes only when every mandatory child passes, fails if any fails and otherwise stays NOT TESTED.

| Test / requirement | Purpose and main evidence |
| --- | --- |
| FWT-01 / FWR-01 | **Readiness and [independent isolation](#c-verify-isolation-and-required-network-access).** Inventory, cables, routes, trust and the protected-boundary mock block. |
| FWT-02 / FWR-02 | **Management, Corporate and Restricted.** Verify [FF-01 through FF-08](../architecture/ARCHITECTURE.md#inter-zone-policy-matrix), default deny and restricted management. Use measured capacity/reserves, console recovery, physical HP routing, same-zone host rules and allow/deny sessions. |
| FWT-03 / FWR-03 | **Directory roles, [six application cases (C01-C06)](#c-test-the-six-application-access-cases) and [revocation](#d-revoke-an-application-permission).** Logon records, Apache decisions and existing/fresh request times. |
| FWT-04 / FWR-04 | **[Endpoint protection](#phase-2-identity-and-endpoint-security) and least privilege.** Builds, updates, antivirus, host rules and standard/admin actions. |
| FWT-05 / FWR-05 | **[HTTPS trust, name and validity](#a-create-and-verify-https-certificates).** CA/leaf inspection and trusted/untrusted browser outcomes. |
| FWT-06 / FWR-06 | **[Remote allow, identity/port denial and revocation](#e-configure-test-and-revoke-tailscale-access).** Grants, device/host policy, sessions and revocation times. |
| FWT-07 / FWR-07 | **[Five security event categories](#a-collect-five-security-events) and one investigation.** DC1, HP and Apache logs, clock comparison and matched policy. |
| FWT-08 / FWR-08 | **[One repeatable capacity automation](#c-run-the-capacity-summary-automation).** Output, OS comparison, safe rejections and before/after state. |
| FWT-09 / FWR-09 | **[One encrypted off-compute APP1 backup and isolated restore](#d-back-up-app1-and-restore-it-in-isolation).** Archive/key custody, manifest, separate clock, HTTPS role checks and cleanup. |
| FWT-10 / FWR-10 | **[Handover and sanitized publication](#d-review-evidence-submit-and-obtain-owner-acceptance).** Ten traceable results, five submissions, manual review and GitHub read-back. |

**CHECK**

Every child has a verdict, evidence and a second technical observation.

**RECORD**

**Deliverable 03 > Requirements Coverage / Evidence Index**. Link results and defects to private evidence. See the [coverage index](../testing/TEST-PLAN.md#coverage-index) and [legacy IDs](../governance/HISTORICAL-REQUIREMENT-TRANSITION.md).

<a id="step-26---finish-the-five-office-deliverables"></a>
<a id="required-lab-deliverables"></a>

### C. Complete the five Office deliverables

**WHERE**

Private copies of the five files, available as blank templates in the [deliverable library](../README.md#editable-lab-deliverable-templates).

**STEPS**

1. Complete every worksheet or section below. Use observed results and link detailed evidence in its owning record.
2. In **05 > Final Evaluation**, apply the [assignment rubric](../assignments/PROJECT-ASSIGNMENT.md#success-criteria). Infrastructure/Network 25, Identity/Access 25, Monitoring/Operations 20, Testing/Recovery 20, Documentation/Submission 10. Total 100.
3. Enter evaluator/date and engineering verifier/evidence cutoff. Award credit only for verified implementation.

| Filename | What to complete | Main evidence source |
| --- | --- | --- |
| `01-Lab-Environment-and-Architecture.xlsx` | Hardware & Readiness, Virtual Machines, Network Zones, Allowed Network Flows, Resource Allocation | Phase 1 records for Dell, physical HP and three workload VMs |
| `02-Identity-and-Zero-Trust-Implementation.docx` | All nine sections from Implementation Overview through Implementation Results and Limitations | Phases 2-3 settings and tests in 03 |
| `03-Security-Monitoring-and-Testing.xlsx` | Security Events, Denied Access Investigation, Test Cases, Requirements Coverage, Automation Verification, Backup & Restore, Evidence Index, Owner Acceptance | Private observations and evidence IDs |
| `04-Troubleshooting-and-Lessons.xlsx` | Issue Log | Failures, approved fixes and retests |
| `05-Final-Project-Submission.docx` | All ten sections from Executive Summary through Supporting Deliverables and Evidence | Findings and limitations from 01-04 |

**CHECK**

All five files have traceable evidence and accurate limits. Correct unsupported claims or broken links before submission.

**RECORD**

**Deliverable 05 > Project Limitations** and **Supporting Deliverables and Evidence**.

<a id="step-27---review-evidence-submit-and-obtain-owner-acceptance"></a>
<a id="phase-5-checkpoint-and-recovery"></a>

### D. Review evidence, submit and obtain owner acceptance

**WHERE**

Approved publication workstation and **Deliverable 03 > Owner Acceptance**.

**STEPS**

1. Inspect every public candidate's name, metadata, hidden content, screenshots and links. Review the staged diff and new Git history. Keep raw logs, actual addresses, inventories, credentials, private keys, working files and backup data outside Git. Preserve private originals.
2. Run the [documentation checks](../governance/DOCUMENTATION-BUILD.md#validation-and-visual-review) and inspect changed PDFs. Publish only reviewed sanitized artifacts. Verify and record observed PR, final-head CI, merge and local/remote synchronization. Follow the [repository workflow](../../AGENTS.md#git-and-github-conventions).
3. Give the owner the five completed files and evidence index. Demonstrate analyst report access, engineer maintenance access, unassigned/revoked denial and approved remote access/revocation. Use approved permissions and recorded revocation evidence.
4. Present measured recovery, integrity and HTTPS role evidence. Discuss limitations and unavailable workflows. Capture the owner's observations, follow-ups and explicit decision.

**CHECK**

Stop publication on a sensitive-data finding and follow the [incident process](../../AGENTS.md#public-repository-and-secrets). All mandatory results must pass for engineering completion. Unresolved critical or high safety issues block acceptance regardless of score. Follow the [Acceptance Criteria](../testing/ACCEPTANCE-CRITERIA.md).

**RECORD**

**Deliverable 03 > Evidence Index** for reviewer/date and publication evidence. In **Owner Acceptance** record reviewer/date, observed usability, limits and confirmation reference. Owner user acceptance testing (UAT) stays **PENDING** without an explicit decision, independent of test results, CI and scoring.
