# Windows directory and policy reference

Use with [Phase 2](../LAB-IMPLEMENTATION-GUIDE.md#phase-2-identity-and-endpoint-security) for FWR-03/FWR-04 and FWT-03/FWT-04. These are proposed procedures, not executed results. Stages E (directory) and F (endpoint) require separate approval naming assets, changes, validation and rollback. Creating a missing workload also needs its applicable host/network scope. Use the dedicated lab administrator path with guest console recovery.

## Required private plan and supported profile

Record the exact supported Windows Server edition/build with Desktop Experience, a supported domain-capable Windows client edition (for example Windows 11 Pro/Enterprise/Education, never Home for domain join), and the selected supported Linux LTS build. Use approved verified media, evaluation/licensing terms and private update/activation records. Screens below assume Windows Server Desktop Experience and Windows 11; review a different release before use. Do not install another product merely because a command is unavailable.

The private plan supplies actual addresses, masks, gateways, NIC MACs, bridge/tags, existing OU/container paths, join authority, administrator rights, DNS/time sources, approved functional levels, password/lockout values, first-logon choices and recovery locations. Symbolic LAB_* fields below are not literal configuration. No home/production trust, federation, synchronization, corporate resolver fallback or credential reuse is permitted.

Have current recovery copies before changes. The separate privileged person may use a temporary local setup identity and a distinct privileged domain identity; neither is a fourth standard/application persona. Keep DSRM and local/domain recovery credentials in approved private custody. Remain disconnected unless exact update/activation egress and independent isolation are approved. Offline servicing and activation must be lawful and supported; missing media, credentials or a safe method blocks dependent work.

## VM profiles and installation

**Target / approval:** Dell Proxmox and guest consoles; named lab administrator with the applicable B/C workload creation and E/F guest approvals. Inspect first; retain working VMs. Create only a missing approved workload, never rebuild an existing one to match this example. A virtual disk is a file-backed guest disk; do not pass through a physical Windows disk.

| VM | Zone | vCPU | RAM MiB | Disk GiB |
| --- | --- | --- | --- | --- |
| DC1 | Corporate | 2 | 6144 | 64 |
| WIN1 | Corporate | 2 | 6144 | 64 |
| APP1 | Restricted | 2 | 4096 | 32 |

1. For each VM choose the approved unused ID, name, storage and verified OS ISO. Set its allocation from the table. Give it one zone NIC and record its MAC. Check selected OS minimums against real host capability; pause for an approved adjustment if they do not fit.
2. For the conditional Windows 11 profile, select **System > BIOS: OVMF (UEFI)**, add an EFI disk with the approved Secure Boot keys and **TPM 2.0** storage. Use an approved supported CPU model. A compatible SATA disk/emulated NIC can avoid separate VirtIO drivers; if VirtIO is selected, attach only verified approved driver media. Never bypass setup requirements.
3. Start DC1 > **Console**. In Windows Server Setup choose the approved edition **with Desktop Experience**, **Custom installation**, and only the empty 64 GiB VM disk. Finish setup and set the local Administrator password privately. Remove the ISO after successful boot. [Microsoft's installation guide](https://learn.microsoft.com/en-us/windows-server/get-started/install-windows-server) distinguishes Desktop Experience from Server Core.
4. Install WIN1's approved domain-capable Windows edition to its own 64 GiB VM disk. Use the approved lab-only setup/activation method and the separate administrator's local setup identity; do not use a corporate/home account or a sign-in bypass. Missing lawful offline setup or safe connectivity is a blocker.
5. Install APP1 using the approved Linux ISO. For the Ubuntu example choose the normal server installation, the 32 GiB virtual disk and hostname **APP1**. Use the same separate privileged person's lab administration identity, not another project persona. Leave optional services, cloud identity integration and SSH off unless specifically approved. Use the Proxmox console for administration.
6. On Windows, **Server Manager > Local Server > Computer name** or **System Properties > Computer Name > Change** sets **DC1/WIN1** before domain work. Restart if asked. Record actual OS/build, media, resources, NIC and update/evaluation status in **01 / Virtual Machines**; do not describe an unactivated system as fully ready.

**Check:** exactly DC1, WIN1 and APP1 are workload VMs on Dell; OPNsense runs physically on HP. Totals are 6 vCPU / 16 GiB / 160 GiB. Each guest boots from its own virtual disk with one zone NIC, matched by bridge/tag/MAC to the private map. RAM/storage reserves still fit. Record selected profile and limitations in **02 / Implementation Overview**.

**If it fails:** use the VM console to check ISO, boot order, virtual disk/controller and supported hardware. Do not alter the host disk, add a VM or disable Windows security requirements to finish setup.

## AD DS and DNS

**Purpose and location:** on DC1 as local Administrator, create **ad.lab.test**, a separate Windows directory. Active Directory (AD) stores Windows users/groups; DNS resolves lab names. This creates a new forest, the top-level directory boundary, under E approval.

1. Open **Server Manager > Local Server > Ethernet > adapter Properties > Internet Protocol Version 4 > Properties**. Enter LAB_DC1_IP, the Corporate mask/prefix and LAB_FW_CORPORATE_IP as gateway. Use LAB_DC1_IP as the planned lab DNS server; it begins serving after promotion. Remove public/corporate alternate resolvers. Confirm the guest is DC1, its MAC matches the approved Corporate bridge/tag record and time/timezone are correct.
2. Open **Manage > Add Roles and Features > Role-based or feature-based installation**. Select DC1, check **Active Directory Domain Services**, accept its management tools and install.
3. Select the notification flag > **Promote this server to a domain controller**. Choose **Add a new forest**, enter **ad.lab.test**, retain **DNS Server** and the approved supported functional levels. Enter the Directory Services Restore Mode recovery password privately.
4. Review DNS options, the proposed NetBIOS name and database/log/SYSVOL paths. A missing parent delegation can be normal for this standalone .test forest; confirm that exact warning, rather than ignoring all prerequisite warnings. Install only after the prerequisite check is understood, then allow the approved restart. [Microsoft's deployment procedure](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/install-active-directory-domain-services--level-100-) governs these choices.

**DESTRUCTIVE / HIGH-RISK - DC1, elevated Windows PowerShell as local Administrator, E approval.** Use this retained minimal alternative only when its selected-release default forest/domain functional levels and paths exactly match the approved plan. Otherwise use the wizard or a separately reviewed command specifying the approved levels; this reference supplies no invented level. This is an alternative to the role/promotion clicks above, not a second deployment. It installs AD tools and creates the same lab forest, prompting securely for recovery credentials and rebooting after promotion. No placeholder or inline password:

```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
Install-ADDSForest -DomainName 'ad.lab.test' -InstallDNS
```

**Check:** after reboot, **Server Manager > Tools** includes AD Users and Computers, DNS and Group Policy Management. In DNS expand **DC1 > Forward Lookup Zones > ad.lab.test** and inspect DC1 and directory service records. A role-install success alone does not prove promotion. Record in **02 / Active Directory and User Roles**, with FWT-03 evidence in **03 / Test Cases**.

**If it fails:** inspect the reported prerequisite, DC1 name, static address, DNS and time. Do not rerun forest creation, suppress checks, demote DC1 or revert a DC snapshot casually. Directory recovery requires an explicitly approved supported plan.

## Directory verification

**READ-ONLY - DC1, elevated Windows PowerShell as the approved directory administrator, E validation scope.** After promotion/restart, inspect the actual forest, functional levels, controller, domain and advertised service records. No replacements:

```powershell
Get-ADForest | Select-Object RootDomain,ForestMode,Domains
Get-ADDomain | Select-Object DNSRoot,DomainMode
Get-ADDomainController -Identity DC1
Get-Service NTDS,DNS,Netlogon
Get-SmbShare -Name SYSVOL,NETLOGON
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.ad.lab.test
```

**Expected:** ad.lab.test is the isolated forest/domain, DC1 is its writable DNS controller, the approved functional levels match, services run, SYSVOL/NETLOGON are shared and the SRV target is dc1.ad.lab.test. Compare with Server Manager/AD Users and Computers and DNS Manager's DC1 A/service records. Inspect DNS Manager **DC1 > Properties > Forwarders** and **Root Hints**: no corporate/public recursive fallback; external resolution stays absent unless separately approved. Inspect DC1's actual selected lab time source/status and Windows time policy before relying on logon. Keep Windows IPv6 stacks intact; review the approved no-routed-IPv6 network baseline.

**Failure / recovery:** a role entry or open console is insufficient evidence of promotion. Inspect prerequisites, event logs, names, DNS and time. Never repeat forest creation, demote/rebuild DC1 or roll back its snapshot to hide failure. Use the separately approved supported directory recovery plan.

## Users groups and permissions

**Purpose and location:** in DC1 **Server Manager > Tools > Active Directory Users and Computers**, create three standard people and one separate administrator. A security group collects permissions; membership alone does not invent a permission.

1. Verify the approved existing OUs/containers and their distinguished paths in the private identity plan. Do not assume the default Users container. If an approved OU is missing, right-click **ad.lab.test > New > Organizational Unit** to create the approved containers for standard users, privileged identities and member computers. An organizational unit (OU) organizes objects and lets you link policy; it is not another network zone. Keep DC1 in **Domain Controllers**.
2. Inspect existing account names and membership first; stop for a conflicting object instead of duplicating it. In the standard-user OU, select **New > User** for **ava**, **eli** and **uma**. Use those logon names, prompted unique private passwords and the approved password-change settings. In the privileged OU create only the separately named administrator. Secure built-in accounts separately; they are not extra project people.
3. Verify existing groups first. For a missing approved group use **New > Group**, **Global** scope and **Security** type for **LabReaders**, **LabMaintainers** and **LabAdmins**. In **Properties > Members > Add**, enter names, **Check Names**, then save the membership below.

| Person | AD group membership | Application role planned later |
| --- | --- | --- |
| ava | LabReaders | Reports |
| eli | LabReaders and LabMaintainers | Reports and maintenance instructions |
| uma | Neither reader nor maintenance group | Neither page |
| Separate privileged administrator | LabAdmins | Infrastructure only; no fourth app account |

4. Under the same approved rights plan, assign **LabAdmins** the required infrastructure rights. For WIN1 local administration, add that group to WIN1's local **Administrators** using the approved local/group-policy setting. Any DC Domain Admins membership must be explicitly covered by E approval; the custom LabAdmins name itself grants no rights. Check ava/eli/uma are absent from privileged built-in groups.
5. Open **Server Manager > Tools > DNS > DC1 > Forward Lookup Zones > ad.lab.test > New Host (A or AAAA)**. Enter **Name: app**, **IP address: LAB_APP1_IP**, replacing it privately. Add the IPv4 A record; do not invent an AAAA record or corporate forwarding. Check **app.ad.lab.test** resolves to the intended Restricted address. [Microsoft documents DNS record management](https://learn.microsoft.com/en-us/windows-server/networking/dns/manage-resource-records?tabs=dns-manager).

**Check:** inspect each group's Members tab and each user's Member Of tab. Exactly three standard users, three project role groups and one separate privileged administrator are recorded in **02 / Active Directory and User Roles**; built-in/service objects are secured but not counted as project personas.

**If it fails:** correct only the wrong entry under the approved change. Preserve the previous membership. Do not grant Domain Admins to a standard user to resolve a logon problem.

## WIN1 domain join and verification

**Purpose and location:** on WIN1 using its approved local administrator, join the separate lab directory so standard users can sign in and receive Windows policy.

1. In WIN1's adapter IPv4 properties, enter LAB_WIN1_IP, Corporate mask and LAB_FW_CORPORATE_IP. Set **Preferred DNS: LAB_DC1_IP**, with no external alternate. Ensure DC1 is running and time agrees.
2. Open **System Properties > Computer Name > Change**. Verify **WIN1**, select **Domain**, enter **ad.lab.test**, and provide the approved lab join credential through the prompt. On confirmation restart, following [Microsoft's domain-join procedure](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/join-computer-to-domain).
3. On DC1, find WIN1 in AD Users and Computers and move it into the approved member-computer OU. On WIN1 choose **Other user**, sign in as **ava@ad.lab.test** and confirm the Windows session uses the lab domain. Test eli and uma logon only within the approved test scope.
4. As the lab administrator, open PowerShell for the bounded checks below. Record name resolution, standard logon and effective policy as separate observations.

**READ-ONLY - WIN1, Windows PowerShell as the approved lab administrator; elevation for the secure-channel check.** DNS queries must show the private DC1/APP1 addresses. The final command checks this member machine's domain relationship; it is not a DC1 health test. No replacements:

```powershell
Resolve-DnsName dc1.ad.lab.test
Resolve-DnsName app.ad.lab.test
Test-ComputerSecureChannel -Verbose
```

**Check:** correct private answers and **True** for the [secure-channel test](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-computersecurechannel?view=powershell-5.1), plus actual standard-user logon and policy. Record configuration in **02 / Active Directory and User Roles** and results in **03 / Test Cases**, FWT-03.

**If it fails:** inspect WIN1's DNS address, DNS records, time, domain name and DC1 host rules. WIN1/DC1 are on the same Corporate segment; an OPNsense allow cannot fix a DC1 host denial. Do not add **-Repair**, rejoin repeatedly or use public DNS without a bounded correction approval.

## Account and endpoint policy

**Purpose and location:** under F approval, use DC1 **Group Policy Management** and Windows firewall/health views to protect DC1/WIN1. Group Policy distributes settings to the domain or selected OUs; a setting is useful only if it actually reaches its target.

The private F approval must supply every selected value; this table is a worksheet, not a default policy. Save previous values and the GPO links/security filters before editing. Inspect the winning values on each target after application; restore only the pilot change through console access if the expected policy or administrator control fails.

| Setting / target | Exact path or selection to record |
| --- | --- |
| Domain passwords | Domain-root GPO > Computer Configuration > Policies > Windows Settings > Security Settings > Account Policies > Password Policy: approved minimum length, history, minimum/maximum age and complexity. |
| Domain lockout | Same Account Policies > Account Lockout Policy: approved threshold, duration and reset interval. |
| WIN1 endpoint | Approved computer OU, GPO name/link/filtering, all firewall profile defaults and Defender selections below. |
| DC1 protection | Inspect effective DC policy, Defender service/protection/signatures, firewall profiles/defaults and enabled directory rules. A WIN1 OU GPO does not configure DC1. |

1. In **Group Policy Management > Forest: ad.lab.test > Domains > ad.lab.test**, create/link the approved lab account-policy Group Policy Object (GPO) at the **domain root**. Edit **Computer Configuration > Policies > Windows Settings > Security Settings > Account Policies**. Enter the owner-approved minimum length/history/age/complexity and lockout threshold/duration/reset values from F approval. Do not invent those numeric values or link domain-account password policy only to a member OU.
2. Create/link the endpoint GPO to WIN1's computer OU. Under **Security Settings > Windows Defender Firewall with Advanced Security > Windows Defender Firewall Properties**, keep Domain/Private/Public profiles **On**, inbound **Block** and only reviewed exceptions. Keep Microsoft Defender protection enabled using **Computer Configuration > Policies > Administrative Templates > Windows Components > Microsoft Defender Antivirus**; do not enable a policy that turns antivirus off.
3. On DC1 and WIN1 open **Windows Defender Firewall with Advanced Security > Inbound Rules**. Inspect enabled built-in AD/DNS rules. In each required rule's **Properties > Scope > Remote IP address**, restrict it to the actual lab clients; check protocol/local service ports and enabled profiles too. If creating a missing rule, use **New Rule > Custom**, exact service/program, protocol/local ports, remote addresses, **Allow**, the reviewed profiles and a clear FF-02 name.

## Scoped service ports

**Target / approval:** DC1 host firewall; E/F-approved directory/endpoint administrator. Apply only the selected dependencies using rule Properties > Scope. Expected: WIN1 logon and policy work without a broad client permit. Preserve prior rule scopes for console rollback.

| WIN1 to DC1 dependency | Destination port to review in DC1 host policy |
| --- | --- |
| DNS | TCP/UDP 53; APP1 may also use only DNS/time under FF-04 |
| Kerberos logon/password service | TCP/UDP 88 and 464 |
| Directory lookup and policy files | TCP/UDP 389; TCP 445 |
| RPC endpoint mapper and dynamic RPC | TCP 135 and the selected modern-server range, normally TCP 49152-65535 |
| Lab time | UDP 123 only if that is the approved Windows time service |
| Global Catalog | TCP 3268 only if selected-version client behavior requires it |

Use [Microsoft's AD service table](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/config-firewall-for-ad-domains-and-trusts) for the selected versions. Do not permit replication/trust/LDAPS services merely because they appear in the vendor's wider table. The dynamic range is a service dependency scoped to WIN1/DC1, not an all-host/all-port permit. Check overlapping default rules do not keep broad remote scope.

## Auditing and effective policy

**Target / approval:** DC1 Group Policy Management, directory administrator, E/F scope. Preserve existing links/filtering and winning values for rollback. Continue the account/endpoint procedure with its target-specific auditing:

4. In the **WIN1 endpoint GPO** edit **Computer Configuration > Policies > Windows Settings > Security Settings > Advanced Audit Policy Configuration > Audit Policies > Logon/Logoff > Audit Logon**, enabling approved success/failure auditing. Create/link the separately approved **DC audit GPO** to the **Domain Controllers** OU, then edit its **Account Logon > Audit Kerberos Authentication Service** success/failure settings under that same advanced-audit path. WIN1's OU policy cannot apply to DC1. Include approved account-management auditing and ensure basic audit settings do not override advanced policy; inspect the effective advanced audit selection on each actual target before Phase 4.
5. On WIN1 use the local policy-result commands below. Check the intended GPOs are applied and WIN1 is in the correct OU; compare specific values with the local effective security-policy/firewall views. In **Windows Security**, inspect antivirus, firewall and update status. Log off/restart only when the approved setting needs it.
## Privilege and protection checks

**Target / approval:** WIN1, F approval; the named administrator and ava in separate sessions. Expected: protection enabled and ordinary-user administration denied, with a working elevated control. On mismatch inspect effective policy/membership; recover only approved pilot settings at console.

6. In **Computer Management > Local Users and Groups > Groups > Administrators**, confirm the three standard users are absent and the approved LabAdmins rights are present. Use the same read-only computer-policy query below as the harmless standard/admin privilege comparison; no configuration write is needed.

**READ-ONLY - WIN1, first in ava's unelevated Windows PowerShell, then in the separate lab administrator's elevated shell.** The first query shows ava's applied user policy. Run the second in each context: expect Access Denied as ava, then a computer-policy summary as the authorized administrator. No passwords/remote target arguments or placeholders. [Microsoft documents gpresult](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/gpresult):

```powershell
gpresult /scope user /r
gpresult /scope computer /r
```

**Check:** the actual user/computer policy and privilege behavior agree with membership. An unexpected standard-user success requires investigation before PASS; a missing policy result requires checking OU/application/logon, not disabling protection. Use the full winning-setting view where the summary alone cannot prove a value.

**Check:** applied policy, enabled protection and scoped rules agree with standard logon, the standard-user denial and approved admin control. Record in **02 / Windows and Linux Endpoint Controls** and **03 / Test Cases**, FWT-04. Record update/activation gaps honestly.

**If it fails:** inspect OU link, security filtering, winning policy, profile and enabled rule scope. Restore only the changed pilot settings through retained administrator/console access. Never disable the firewall or antivirus as a shortcut.

## Recovery and version notes

Use the failure/recovery instructions in each section above. Keep the separate administrator and console working before policy changes. Inspect nested privileged membership as well as direct membership; never elevate ava, eli or uma. Directory rebuild, demotion and snapshot rollback require their own supported recovery approval.

Inspect **Windows Security > Virus & threat protection**, **Firewall & network protection** and Windows Update/build on DC1 and WIN1. Confirm Defender real-time protection/signatures and all firewall profiles. Use **Group Policy Management > Group Policy Results** or a local winning-setting view when gpresult /r cannot prove a value. Record unsupported or absent tooling as a gap.

FWT-03.01-.03 do not pass the six Apache cases or revocation: Phase 3 uses separate accounts, distinct passwords and manual role mapping. FWT-04 also requires Linux, updates, firewall/adapters and the harmless privilege test. In **03 > Test Cases**, record actuals, operator/date/build, evidence, second observation and verdict; summarize in **02** and log issues in **04 > Issue Log**. Missing work stays NOT TESTED.

Check [Windows Server setup](https://learn.microsoft.com/en-us/windows-server/get-started/install-windows-server), [Windows 11 requirements](https://www.microsoft.com/en-us/windows/windows-11-specifications), [AD functional levels](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/active-directory-functional-levels) and [AD deployment](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/install-active-directory-domain-services--level-100-) for the selected release. Retain supported CPU, UEFI/Secure Boot capability, TPM 2.0 and published RAM/storage minimums. Server Core needs a reviewed administration alternative. Verify the read-only [forest](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adforest?view=windowsserver2025-ps), [domain](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomain?view=windowsserver2025-ps), [controller](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomaincontroller?view=windowsserver2025-ps) and [share](https://learn.microsoft.com/en-us/powershell/module/smbshare/get-smbshare?view=windowsserver2025-ps) cmdlets against that build before use.
