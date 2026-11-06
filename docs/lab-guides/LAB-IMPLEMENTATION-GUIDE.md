# Lab implementation guide: five phases

**T6 baseline, 2026-11-06. Implementation PLANNED; operational controls NOT TESTED; owner user acceptance testing (UAT) PENDING.**

This guide supports the [four-week assignment](../assignments/PROJECT-ASSIGNMENT.md). Read the [architecture](../architecture/ARCHITECTURE.md), [security controls](../security/SECURITY-REQUIREMENTS.md) and [test plan](../testing/TEST-PLAN.md) together. T6 changes documents only; none of the implementation examples below has been executed.

## How to execute a future approved stage

Before each stage record owner approval/date, exact assets, permitted changes, validation, private evidence handling and rollback in a new draft [task report](../reports/INDEX.md). Verify current installed-version guidance, media integrity and lawful terms. Five phases organize work; they retain the separate A-L approvals in [AGENTS.md](../../AGENTS.md).

| Phase | Existing approval stages retained | Week |
| --- | --- | --- |
| 1: Infrastructure and Network | A readiness, B host, C networking, D virtual firewall; each separately | 1 |
| 2: Identity and Endpoint Security | E directory, F endpoint/server baselines | 2 |
| 3: Zero Trust Access Controls | G simple CA, H application roles, I Tailscale | 2-3 |
| 4: Monitoring, Automation and Recovery | J monitoring; L automation/recovery portion | 3-4 |
| 5: Validation and Final Submission | K validation; remaining L closeout portion | 4 |

T6 replaces old stage quantities, not approval gates. Only the explicitly approved automation/recovery portion of L may precede K; prior approval does not authorize remaining changes. Allow about 8-12 focused hours weekly after readiness/approvals. Pause dependent work on delivery, isolation, activation or recovery gaps and revise dates.

All implementation examples are **proposed future commands/configuration**, with targets stated. Set symbolic variables privately to reviewed lab-only values outside Git. Stop on uncertain assets/disks, unexpected protected connectivity, secret output, missing rollback or failed safety checks. Use approved console isolation and retain private evidence. Never execute a guide merely because it exists.

## Phase 1: Infrastructure and Network

### Prerequisites

Stage A read-only approval first. Existing owner-described hardware: Dell Precision 5820 (W-2125, 80 GB RAM, 512 GB SSD), Lenovo laptop, HP desktop, test laptops and Google Wifi; thermal paste available.

**Ordered:** Xeon W-2145, Samsung 1 TB SSD, Sabrent PCIe adapter, Intel I350-T4 NIC, GL.iNet Beryl AX and TP-Link managed switch. Reference: latest owner procurement plan and 2026-11-06 procurement correction. **Delivered:** unconfirmed; expected November 7 for non-CPU items and November 12, 2026 for CPU. **Installed:** no T6 installation evidence or assumption that Proxmox/other lab software exists. **Validated:** no hardware-readiness/operational-lab evidence. Do not reorder these items.

Before installation confirm delivery, physically inspect parts, verify compatibility, inventory existing data/services, establish backup/recovery readiness and obtain exact owner approval for destructive changes. Verify CPU/cooler/firmware and SSD/adapter/slot compatibility. Preserve original Windows disk and existing services; shutdown/migration requires separate approval. Extra hardware does not mandate physical OPNsense, VLANs or extra zones.

### Required tools

Existing inventory/firmware/storage screens, physical console, private parts/disk/cable ledger, verified official media/checksums, private credential store and recovery media. No new inspection software during read-only A.

### Implementation instructions

1. **A:** inspect CPU/RAM/virtualization, disk identity/contents/free space, NICs and console. Compare supplied/observed facts and date each hardware status separately. Do not open an installer.
2. Inventory current services/data and availability needs. Verify backup/recovery; exclude protected workloads before any approved host transition.
3. Recalculate the [capacity ledger](../architecture/ARCHITECTURE.md#initial-capacity-budget): four VMs, 20 GiB guest RAM/176 GiB disks, 12 GiB host RAM and 80 GiB free disk reserved, plus media/restore space. Issue no-go if it cannot fit.
4. Map cables/bridges and administrator adapters. No forwarding via Wi-Fi, another NIC or VPN; no workload bridge physical uplink. Keep external access disconnected.
5. **B:** after exact-disk/destructive-install approval and verified recovery, boot official verified Proxmox media at console. Recheck disk identity immediately before selection; never use the preserved Windows disk or unapproved substitute.
6. Configure one host with named scoped administration, supported MFA/recovery and isolated management. Record build/updates/storage and console recovery. Root is for necessary setup/recovery. No cluster.
7. **C:** create vmbr0 Management, vmbr10 Corporate and vmbr20 Restricted. Only vmbr0 has the verified isolated physical admin segment/host IP. Save prior settings and apply from console.
8. **D:** create OPNsense (2 vCPU/4 GiB/16 GiB), one NIC per zone. Match recorded virtual MAC/interface identities; install verified media. Optional WAN remains disconnected; no inbound forwarding.
9. Apply [FF-01 through FF-08](../architecture/ARCHITECTURE.md#inter-zone-policy-matrix), replacing broad installer permits with exact source/destination/service allows. Keep the named management allow path before narrowing rules.
10. Inspect automatic/floating/group/anti-lockout rules, states, NAT, DNS, IPv6, firewall-originated traffic and UPnP/NAT-PMP. Save encrypted private config. Internet dependencies await approved independently isolated egress.

Proposed read-only inventory on **approved Windows candidates**, output private:

```powershell
Get-CimInstance -ClassName Win32_ComputerSystem
Get-CimInstance -ClassName Win32_Processor
Get-NetIPConfiguration -All
```

Use version-matched [Proxmox/OPNsense guidance](../governance/REFERENCES.md); no shortcut disk-selection or packet-filter-disable command.

### Expected results

Verified readiness and, only after B-D approvals, one recoverable host/firewall, three zones and no protected-network path. Hardware states reflect observations.

### Verification steps

FWT-01/FWT-02: compare cables/bridges/NICs/routes/IPv6/aliases and effective policy with permitted/denied bounded flows to known listening **lab-owned mocks**; inspect logs/counters. Repurpose approved guests/console, no permanent extra VMs. Never probe home/production. Verify named administration, ordinary-user denial and console recovery.

### Troubleshooting

Lost administration: inspect interface mapping/specific allow from console. Unexpected permit: disconnect approved egress, inspect states/automatic rules/forwarding. Uncertain disk/compatibility/backup blocks installation; no substitute disk/home uplink.

### Rollback procedures

A is read-only. For B-D restore specific saved host/firewall/network settings from console; keep egress disconnected until reverified. Destructive reinstall/hardware changes need explicit rollback coverage. Preserve data/evidence.

## Phase 2: Identity and Endpoint Security

### Prerequisites

Phase 1 verified; E/F approvals; supported lawful Windows Server/Windows/Linux media, approved update/activation path, private DNS/address/time and recovery custody.

### Required tools

Proxmox console; Server Manager, Active Directory Users and Computers, DNS/Group Policy Management; supported Linux/Windows firewall/settings tools and baseline checklist.

### Implementation instructions

1. Create DC1 in Corporate (2 vCPU/6 GiB/64 GiB), WIN1 in Corporate (2/6/64), APP1 in Restricted (2/4/32). Each has one zone NIC; check supported CPU/disk/virtual TPM needs before installation.
2. Install approved OSs, record builds/update status/evaluation deadlines and configure lab DNS/time. Missing safe activation remains a dependency.
3. On DC1 set fixed private address/name, install AD Domain Services/DNS and create ad.lab.test. Use secure Directory Services Restore Mode prompts/private custody; no corporate trust/cloud join/sync.
4. Create user/privileged/computer organizational units. Add standard **ava**, **eli**, **uma**, plus one separate named privileged admin. Three project security groups: **LabReaders** (ava, eli), **LabMaintainers** (eli), **LabAdmins** (admin). Delegate only required rights. Secure built-in/service accounts separately; they are not extra project personas.
5. Join WIN1 to the lab domain; use lab DNS only. Add APP1's DNS record; APP1 uses approved lab DNS/time without a domain join.
6. Pilot Group Policy for host firewall, supported antivirus, audit logon/account changes (including DC Kerberos Authentication Service success/failure), sensible password/lockout and standard/admin separation. Protect recovery accounts; no lockout/password-attack experiment.
7. Enable APP1 host firewall; HTTPS only from approved sources, administration only from the dedicated path. Disable unnecessary listeners/forwarding; retain logs.
8. Inspect resultant policy/local Administrators. Record supported directory recovery as a dependency; snapshots do not prove AD disaster recovery.

Proposed **DC1 elevated PowerShell**, E approval only; changes configuration and may reboot:

```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
Install-ADDSForest -DomainName 'ad.lab.test' -InstallDNS
```

Check selected-version parameters/prompts in [Microsoft guidance](../governance/REFERENCES.md#active-directory-dns-and-policy). Proposed read-only **WIN1 member** check: `Test-ComputerSecureChannel -Verbose`; not a DC health test.

### Expected results

One directory, three standard users/groups, separate privileged admin, Windows member and hardened Linux server. AD Windows sign-in and app permissions are verified separately.

### Verification steps

FWT-03/FWT-04: compare directory/DNS/groups with WIN1 standard logon, name resolution, resultant policy and harmless privileged-action denial. Inspect firewall/patch/antivirus state and trust/cloud/resolver settings; never contact protected assets.

### Troubleshooting

Join/logon/policy failure: inspect lab DNS/service records, time and AD/host rules. WIN1/DC1 share Corporate, so OPNsense does not mediate their traffic. No corporate DNS/credentials or broad permits.

### Rollback procedures

Restore only changed pilot policy/group/host settings, preserving console/admin access. Forest rebuild/demotion or directory restore needs a separately approved supported plan; do not casually revert DC snapshots.

## Phase 3: Zero Trust Access Controls

### Prerequisites

Phase 2 verified; G/H/I approvals; app.ad.lab.test, frozen six-case matrix and private keys/passwords/trust scope. Tailscale requires approved independently isolated Internet, separate lab tailnet/identities, supported MFA/recovery and current terms; otherwise remote checks stay NOT TESTED.

### Required tools

Supported Apache HTTP Server 2.4 file/group authorization and TLS, OpenSSL 3.x, lab browser/clients, AD group view and Tailscale console/client. Verify distribution package/config paths and installed help before approved installation.

### Implementation instructions

1. On APP1 create root-owned synthetic pages in /srv/labapp/reports and /srv/labapp/maintenance. Maintenance-page reading is the restricted engineering workflow; expose no shell/real operational change.
2. **G:** create one encrypted CA key/public root on an approved isolated signing workstation; keep files offline outside Git. Transfer reviewed CSR/public certificates via approved media. No CA VM/separate issuer.
3. Generate APP1 key/CSR, restrict key permissions, inspect/sign the CSR offline with CA:FALSE, serverAuth, proper key usage and DNS SAN app.ad.lab.test. Return public leaf only.
4. Import public CA into approved lab clients; inspect hostname/dates. No home/production trust change or DC time manipulation.
5. **H:** create Apache accounts ava/eli/uma with prompted app passwords different from AD. Restrict hashed password/group files outside the document tree. Manually mirror LabReaders/LabMaintainers; LabAdmins is infrastructure-only. This is not AD SSO/automatic synchronization.
6. Configure one HTTPS virtual host, correct key/leaf, no plain HTTP/public access, listing off, two protected paths and secret-free access/error logs. Syntax-check before supported activation/reload.
7. Execute the six [FWT-03 cases](../testing/TEST-PLAN.md#six-application-access-cases). Remove eli from app LabMaintainers and corresponding AD role; authenticated and fresh maintenance requests must fail. Record time/cache treatment. Restore only under approval.
8. **I:** confirm separate lab tailnet/MFA/recovery, replace permissive defaults, inspect all grants/ACLs/tag owners, then enroll APP1/one approved client. Grant exact APP1 TCP 443 only.
9. Keep subnet advertisements, exit nodes, public sharing, Tailscale SSH/Funnel/Serve and forwarding off. Inspect effective overlay host rules/vendor precedence; OPNsense alone cannot prove overlay restriction.
10. Map app.ad.lab.test privately to APP1 overlay address on the remote client; local clients use zone address. Test permitted/unauthorized/wrong listening port, remove client authorization/grants, and verify existing/fresh session denial. Record actual time and stop on broader access.

Proposed **offline signer**, G approval; private path variables, interactive encrypted-key prompt:

```sh
openssl req -x509 -newkey rsa:3072 -sha256 -days 365 -keyout "$LabCaKeyPath" -out "$LabCaCertPath" -subj "/CN=HL-CYB-001 Lab CA" -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign"
```

Proposed **APP1** key/CSR; restrict filesystem access to the unencrypted service key:

```sh
openssl req -new -newkey rsa:2048 -noenc -keyout "$LabAppKeyPath" -out "$LabAppCsrPath" -subj "/CN=app.ad.lab.test"
```

Private reviewed leaf extension file on **offline signer**:

```ini
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:app.ad.lab.test
```

Proposed **offline signer**, signing and inspection:

```sh
openssl x509 -req -in "$LabAppCsrPath" -CA "$LabCaCertPath" -CAkey "$LabCaKeyPath" -CAcreateserial -CAserial "$LabSerialPath" -days 90 -sha256 -extfile "$LabLeafExtensionsPath" -out "$LabAppCertPath"
openssl verify -CAfile "$LabCaCertPath" -verify_hostname app.ad.lab.test "$LabAppCertPath"
openssl x509 -in "$LabAppCertPath" -noout -dates -ext subjectAltName
```

Browser TLS is a second observation. Certificate revocation infrastructure is excluded; app/device revocation remains mandatory.

Proposed **APP1** password creation: `htpasswd -B -c /etc/labapp/users ava` once, then `htpasswd -B /etc/labapp/users eli` and similarly uma. -c overwrites records; never reuse it to add users. Passwords stay interactive. Private group file:

```text
LabReaders: ava eli
LabMaintainers: eli
```

Proposed **APP1 Apache 2.4 fragment**, after modules/paths are verified; add Listen 443 once and disable default/plain-HTTP sites:

```apache
<VirtualHost *:443>
    ServerName app.ad.lab.test
    DocumentRoot "/srv/labapp"
    SSLEngine on
    SSLCertificateFile "/etc/labapp/app.crt"
    SSLCertificateKeyFile "/etc/labapp/app.key"
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    <Directory "/srv/labapp">
        Options -Indexes
        AllowOverride None
        AuthType Basic
        AuthName "HL-CYB-001"
        AuthBasicProvider file
        AuthUserFile "/etc/labapp/users"
        AuthGroupFile "/etc/labapp/groups"
        AuthzSendForbiddenOnFailure On
        Require all denied
    </Directory>
    <Directory "/srv/labapp/reports">
        Require group LabReaders
    </Directory>
    <Directory "/srv/labapp/maintenance">
        Require group LabMaintainers
    </Directory>
</VirtualHost>
```

Default AuthMerging Off lets child authorization replace parent denial; inspect inherited/global policy. No broad Require valid-user. Configure package-appropriate logs. Proposed APP1 check: `apachectl configtest` (wrapper may differ); Syntax OK does not prove authorization. Proposed enrolled-device inspection: `tailscale status`, output private. See [primary references](../governance/REFERENCES.md).

### Expected results

One CA/leaf, two protected paths, six role cases, app revocation and separate remote permit/deny/revoke evidence. No live AD integration/universal MFA/enterprise certificate lifecycle claim.

### Verification steps

FWT-03/FWT-05/FWT-06: compare page behavior to effective roles/logs; allowed content renders, unauthorized content does not, with intended denial (normally 403 here). Inspect chain/name/dates and untrusted-client failure. Inspect vendor/host rules plus actual wrong-port denial to known listening lab service. Revoke existing/new requests, recording state/cache handling.

### Troubleshooting

TLS: check SAN/chain/dates/trust/private DNS; clicking through warnings is not PASS. App: check spelling, group file, inherited rules/logs/browser credentials; AD alone does not update app roles. Remote: inspect lab tailnet, grants, overlay rules and approved egress; no broad routes/allow-all.

### Rollback procedures

Restore saved app/group settings, syntax-check/reload. Remove trust only from approved clients as needed. Disable remote grant/device, stop client, restore lab DNS/routes and close temporary egress under approval. Preserve failures; exposed keys invoke the owner's authorized credential process.

## Phase 4: Monitoring, Automation and Recovery

### Prerequisites

J and specific L automation/recovery approvals, private records, one operation/target, encrypted off-compute storage, disconnected restore bridge and temporary capacity. Approval identifies exact APP1 targets; no AD/host disaster recovery implied.

### Required tools

Firewall live log, DC1 Event Viewer, Apache logs, existing PowerShell/Python, Proxmox Backup/Restore UI, encrypted storage, hashes and independent clock. No SIEM/collector VM.

### Implementation instructions

1. Use firewall, DC1 Security and Apache access/error sources. Two sources require approved selection covering all five categories. Restrict log access/export, rotate within disk capacity and record UTC/time differences.
2. Generate five benign events: directory success, one single failed logon in disposable synthetic context, app allow, authenticated app denial and firewall denial to a known lab listener. No password attack.
3. Record source/type/context, source/observer times and private evidence ID. Investigate one denial: requested action, rejecting rule/group, working control, correlated evidence and conclusion. On DC1 use the approved account-logon audit view: Kerberos 4768 success and 4771 failed pre-authentication are candidate records; confirm actual event generation from WIN1 and avoid cached/offline logon as the success observation. No enterprise latency/retention target.
4. Define one **local WIN1 capacity-summary operation** using PowerShell/Python. Review hostname/domain allowlist, read-only inputs, private output and invalid target/path rejection before future coding. No remote credentials; one JSON/CSV outside Git.
5. Run the future approved operation, compare output to Windows storage UI and repeat. Measurements may change; only intended output may be replaced, with no configuration/account/network change. Test rejection safely.
6. Define APP1 backup manifest: pages, Apache config, hashed accounts/groups, server key/leaf and public root. Use one consistent full-VM backup on **encrypted off-compute storage**; ordinary Proxmox archive format alone is not encryption.
7. Stop APP1 cleanly for the approved backup mode/target. Verify completion/readable manifest/private recovery-key access. Preserve the only valid backup; same-disk snapshots do not qualify.
8. Restore to an approved temporary VM ID with NICs disconnected, original APP1 off and copied Tailscale inactive. This copy serves the required test only; never connect duplicate identities.
9. Measure restore start to usable-service/data checks. By console/isolated client compare hashes/content, HTTPS and allowed/denied roles. If needed repurpose WIN1 onto a disconnected test bridge under approval, then restore attachment. No Management/home connection.
10. Record age, actual recovery time, scope/verdict/exclusions. APP1 restore does not prove AD/CA/host recovery or enterprise RPO/RTO. Leave copy disconnected; resuming original/deleting copy needs approved cleanup.

Proposed **WIN1 only, L automation approval**, save as a reviewed private script. Pass an existing approved private output directory outside every Git checkout. This one operation reads local capacity and replaces only its named summary; it changes no lab configuration.

```powershell
param([Parameter(Mandatory)][string]$OutputDirectory)
$system = Get-CimInstance -ClassName Win32_ComputerSystem
if ($system.Name -ne 'WIN1' -or $system.Domain -ne 'ad.lab.test') {
    throw 'Target is outside the approved lab operation.'
}
$directory = Get-Item -LiteralPath $OutputDirectory -ErrorAction Stop
if (-not $directory.PSIsContainer) { throw 'Output must be a directory.' }
$cursor = $directory
while ($null -ne $cursor) {
    if (Test-Path -LiteralPath (Join-Path $cursor.FullName '.git')) {
        throw 'Keep the capacity record outside Git.'
    }
    $cursor = $cursor.Parent
}
$capacity = Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType=3' |
    Select-Object DeviceID, Size, FreeSpace
$capacity | ConvertTo-Json |
    Set-Content -LiteralPath (Join-Path $directory.FullName 'WIN1-capacity.json') -Encoding utf8
```

Keep the script/output private until reviewed; a path check is not a substitute for approved target/storage selection. Independently compare byte values to the storage UI, inspect the intended output replacement after two runs, and confirm rejected targets/paths do not write an output.

Proposed **read-only APP1** log inspection:

```sh
journalctl --since today --no-pager
```

Apache request logs have a separate package path. Keep output private. T6 creates/runs no lab automation.

### Expected results

Five events, one explained denial, one safe repeat-run operation and one successful isolated restore with measured limits.

### Verification steps

FWT-07/FWT-08/FWT-09: compare logs to actual actions, automation to another OS view/unchanged configuration, restore output to independent clock/hashes/real HTTPS roles. Keys/backup bytes remain private.

### Troubleshooting

Missing logs: inspect audit/filter/time/rotation. Automation mismatch: inspect target/path/units before retry. Failed restore: preserve original/backup, inspect decryption/storage/version/mode in isolation; do not reconnect to bypass dependencies.

### Rollback procedures

Restore specific changed audit/rotation settings without clearing logs. Remove only intended automation output if approved. Keep copy off/disconnected; resume original only via approved isolation/recovery. Never overwrite sole backup/delete evidence.

## Phase 5: Validation and Final Submission

### Prerequisites

K/remaining L closeout approval, frozen cases, implementation records, current backup, synthetic targets and private custody. T7 files must exist before final project submission; this does not authorize T7 in T6.

### Required tools

[Ten-test catalog](../testing/TEST-PLAN.md), [acceptance criteria](../testing/ACCEPTANCE-CRITERIA.md), clients/policy/log views, evidence index and future T7 files. Git/Python tools support publication only.

### Implementation instructions

1. Freeze expectations and execute every subcheck. Record actual result/time/version/verifier/evidence and second observation. Never change expectation to hide failure.
2. Cover six app cases/revocation, Tailscale permit/deny/revoke, HTTPS, events, automation and restore with bounded lab-owned requests. No scans/protected targets.
3. Mark subchecks PASS, FAIL or NOT TESTED. Timeout without working control/intended denial evidence is insufficient. Preserve failures; corrections/retests need bounded approval.
4. Map ten FWR requirements to evidence/defects. Missing mandatory checks block engineering completion; critical failures block acceptance. Independent human review requires another participant.
5. Complete the five future T7 files below when separately created; own details once and cross-reference. [Project final report](../final-report/FINAL-REPORT.md) remains a template until real implementation/reporting is authorized.
6. Review public artifacts/metadata, complete tracked set, staged diff/new history. Keep secrets, addresses, logs, inventories, backups/keys and filled private working records outside Git.
7. Run repository checks, visually inspect changed PDFs, publish branch/PR, verify exact-head CI/review rules, merge with verified noreply identities and fast-forward main. Compare live IDs.
8. Record the owner's explicit workflow UAT reference/date separately. No score/engineering/CI pass supplies acceptance. Stop at scope boundary.

Repository-only T6 checks, not operational tests:

```powershell
python scripts/validate_docs.py --require-finalized
python scripts/validate_office_templates.py
python scripts/build_docs.py --check --rebuild-check
python -m unittest discover -s tests -v
git diff --check
```

### Expected results

Complete evidence, accurate grading, sanitized submission and separate owner decision. T6 delivers documentation/publication only; operational actuals remain empty.

### Verification steps

FWT-10 checks traceability, public hygiene, GitHub/CI and defects. The [single rubric](../assignments/PROJECT-ASSIGNMENT.md#success-criteria) totals 100; plans earn no implementation credit and UAT stays PENDING until explicit confirmation.

### Troubleshooting

Correct editable source/build code and regenerate for link/PDF errors; no hand-edited hashes. Satisfy PR reviews/checks without force/bypass. Incomplete UAT stays pending.

### Rollback procedures

Reviewed reverts preserve finalized reports/evidence. End temporary policies/tests only under approved cleanup. Never rewrite history/delete owner work/start a stage to close a report.

## Five future T7 deliverables

The **approved T7 target, not yet created**, is under `docs/deliverables/`. Existing eight T5 shells remain unchanged and describe the retired baseline; T7 needs separate authorization.

| File | Owning record |
| --- | --- |
| `01-Lab-Environment-and-Architecture.xlsx` | Status, four VMs/three zones, flows/capacity |
| `02-Identity-and-Zero-Trust-Implementation.docx` | AD/groups, endpoints, HTTPS, six cases/app and remote revocation |
| `03-Security-Monitoring-and-Testing.xlsx` | Five events, investigation, tests, automation/restore |
| `04-Troubleshooting-and-Lessons.xlsx` | Defects, fixes/retests and lessons |
| `05-Final-Project-Submission.docx` | Results/index, rubric, limits and separate UAT |

## Historical requirement and test transition

FWR/FWT identify T6. Old R01-R16/T00-T20 keep their meanings in frozen reports/history/T5 shells; no historical PASS transfers to a new operational test. Old quantities below are historical, not current work.

| Earlier requirement | New requirement | Consolidation or retirement |
| --- | --- | --- |
| R01 | FWR-01 | Isolation retained |
| R02, R03, R04 | FWR-02 | Capacity/admin; six zones become three |
| R05, R08 | FWR-03 | Six standard/two privileged users become three/one; twelve cases become six plus revocation |
| R06 | FWR-04 | Windows endpoint/Linux app, no extra endpoint |
| R07 | FWR-05 | Two-tier/revocation service becomes one CA/leaf, trust/expiry |
| R09 | FWR-06 | Dual pilots become one-resource Tailscale |
| R10 | FWR-07 | Six sources/twenty-event latency/retention targets become two or three sources/five events/investigation |
| R12 | FWR-08 | Two operations become one |
| R13 | FWR-09 | Enterprise objectives become measured APP1 restore |
| R11, R14, R15, R16 | FWR-10 | Hygiene, focused evidence, governance/submission/UAT retained |

| Earlier tests | New test | Treatment |
| --- | --- | --- |
| T01, T02, T03 | FWT-01; capacity also FWT-02 | Isolation/readiness/conditional egress using mocks |
| T04, T05, T06 | FWT-02 | Management/permits/default deny/same-zone host controls |
| T07, T08, T12 | FWT-03 | AD, six app cases and app revocation |
| T09 | FWT-04 | Endpoint baseline |
| T10, T11 | FWT-05 | Trust/name/expiry; certificate-revocation test retired |
| T13, T14 | FWT-06 | Tailscale only; Twingate retired |
| T15, T16 | FWT-07 | Time notes/five events/investigation |
| T18 | FWT-08 | One operation plus repeat/rejection |
| T19 | FWT-09 | APP1 restore, actual time/limits |
| T00, T17, T20 | FWT-10 | Publication/traceability/separate UAT |

See [decisions](../governance/DECISIONS.md), [risks](../governance/RISKS.md) and [end-to-end coverage](../testing/TEST-PLAN.md#coverage-index). High availability/clustering remain excluded.

## T6 stop

Finish sources/PDFs, checks, Markdown-only report and reviewed GitHub synchronization. Do not install hardware/software, select disks, create VMs, change networks, deploy AD/enroll Tailscale, run security tests or begin T7. Await owner review.
