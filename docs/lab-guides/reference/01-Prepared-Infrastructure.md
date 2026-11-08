# Prepared infrastructure reference

Use this reference with [Phase 1](../LAB-IMPLEMENTATION-GUIDE.md#phase-1-prepared-infrastructure). It explains how to inspect the [approved architecture](../../architecture/ARCHITECTURE.md), preserve recovery and collect evidence for FWR-01/FWR-02 and FWT-01/FWT-02. It is not an installation recipe. Read-only review needs stage A approval; host, network and firewall changes need separate B, C and D approval. Active traffic needs its own relevant stage/validation scope, including K where applicable.

## Required private records

Have the selected software builds, switch hardware revision, device identities, cable/port map, nonoverlapping subnets, VLAN IDs, tagged/untagged membership, port default VLAN IDs (PVIDs), NIC/interface/bridge names, administrator path and recovery copies. These are prerequisites; this public reference supplies no private mapping or credentials.

Use the guide's symbolic values in later procedures only after private assignment: LAB_MGMT_CIDR, LAB_CORPORATE_CIDR, LAB_RESTRICTED_CIDR; LAB_ADMIN_IP, LAB_PVE_IP, LAB_FW_MGMT_IP; LAB_FW_CORPORATE_IP, LAB_FW_RESTRICTED_IP; LAB_DC1_IP, LAB_WIN1_IP, LAB_APP1_IP; LAB_PREFIX_LENGTH, LAB_NETMASK and LAB_NIC. Match NICs by the private hardware address. LAB_TIME_IP/LAB_TIME_PORT name only the selected lab time service. LAB_APP_OVERLAY_IP/LAB_REMOTE_OVERLAY_IP need separate remote-access approval. Record backup paths, key custody and unused recovery IDs privately.

Compare current data/services, original Windows disk protection, backup contents/date and console recovery with **01 > Hardware & Readiness**. Read representative backup files from the separate copy; a write-based recovery rehearsal needs exact approval. No disk selection, installer, firmware change or service interruption follows from this reference. Any future destructive work requires the exact disk identity and recoverable backup plan first.

## Physical map and Proxmox bridges

| Inspect | Match against the private map |
| --- | --- |
| Cables and switch | Beryl AX is upstream of physical HP OPNsense; TP-Link TL-SG108E carries separated zones between HP, Dell and the dedicated administrator path. Review every connected port, including unused/extra uplinks. |
| HP > Interfaces > Assignments | Each Management, Corporate and Restricted assignment matches its physical port or approved tagged interface. Review its address and enabled protocol without saving. HP is the sole inter-zone router; no firewall guest is required. |
| Dell node > System > Network | Bridge ports, VLAN awareness, addresses and gateway match the private map. Each workload zone has a physical path to HP; an internal-only bridge is insufficient. Management contains only the approved management attachment. |
| DC1/WIN1/APP1 > Hardware > Network Device | DC1/WIN1 attach to Corporate; APP1 to Restricted. Match bridge/tag and one zone NIC each. No virtual disk passes through the preserved Windows disk. APP1 alone may later add the separately approved overlay. |
| Switch > VLAN > 802.1Q VLAN / 802.1Q PVID Setting | Tagged membership on shared links, untagged/access membership and each port's PVID preserve the same zone end to end. A port label alone proves nothing. Use the manual for the actual revision. |

Workload bridges carry no Proxmox host IP, gateway or routing role. The switch and Dell must not route between zones or bridge zones together. Check the actual bridge/tag/PVID combination, including untagged traffic; three zones do not imply fixed bridge names or a mandatory six-VLAN build.

Compare **Dell node > Summary**, storage > **Summary** and **Datacenter > Storage** with the [architecture budget](../../architecture/ARCHITECTURE.md#initial-capacity-budget): DC1 2 vCPU/6 GiB/64 GiB, WIN1 2/6/64, APP1 2/4/32. Guest totals are 6 vCPU/16 GiB/160 GiB; HP capacity is assessed separately. Retain at least 12 GiB host RAM and 80 GiB free storage; the provisional 320 GiB ledger includes host/media/temporary restore space before filesystem overhead. Thin provisioning creates no space; inspect actual use, snapshots and logs.

For an optional second inventory observation, compare these results with the GUI and private physical/firmware record. Do not publish the output.

**READ-ONLY - dedicated Windows lab administrator computer, local PowerShell; standard user unless separately approved elevation is needed.** These commands inspect that computer only, not the Dell or HP remotely:

```powershell
Get-CimInstance -ClassName Win32_ComputerSystem
Get-CimInstance -ClassName Win32_Processor
Get-NetIPConfiguration -All
```

## Management access

Use only the dedicated lab administrator station, separate lab credentials and approved named management addresses. Keep Dell and HP consoles available. Inspect Proxmox **Datacenter > Permissions** for the named administrator's actual role/path, supported second factor and recovery; a custom group name grants no implicit rights.

At **Datacenter > Firewall** and **Dell node > Firewall**, inspect the selected backend, enabled state, input default deny, explicit administrator-source permits and effective inherited rules. Proxmox HTTPS uses TCP 8006; use OPNsense's actual configured HTTPS port. SSH is permitted only when explicitly approved. Review automatic `local_network` behavior and any `management` IPSet: neither may leave a broad source or extra management service. Do not copy a fixed bridge/interface name from an older example.

In OPNsense, inspect management listeners, ingress policy, automatic and anti-lockout rules. Same-zone Management traffic may never reach OPNsense; Proxmox/device local policy must also restrict it. Narrowing a rule or enabling policy is a separately approved change requiring a working exact administrator permit and console recovery first. Later validation needs both a new allowed administrator session and ordinary-user network denial; missing credentials alone does not prove denial.

## Default deny and allowed flows

Read the complete [FF matrix](../../architecture/ARCHITECTURE.md#inter-zone-policy-matrix). Inspect **Firewall > Aliases**, **Firewall > Rules**, **Firewall > NAT**, **Firewall > Diagnostics > States** and **Firewall > Log Files > Live View** using the selected release's screens. Review interface ingress, floating/group/automatic rules, effective order/quick behavior, translations, existing states, listeners and firewall-originated traffic. Protected-destination blocks precede any approved egress permit. Static aliases do not establish independent isolation.

| Flow | Required restriction and observation |
| --- | --- |
| FF-01 | Only the named administrator reaches named management services; local host/device policy also protects same-zone paths. Supported multifactor authentication and console recovery remain required. |
| FF-02 | WIN1 to DC1 only for selected AD/DNS/time dependencies; same Corporate zone, so inspect Windows host firewalls separately. Match the selected-version service table and Phase 2's host rules; no all-host/all-port allow. |
| FF-03 | WIN1 to APP1 TCP 443 only; physical OPNsense, Linux host policy and application roles all apply. |
| FF-04 | APP1 to DC1 DNS TCP/UDP 53 and only the selected time service. No other directory access or Linux domain join follows. |
| FF-05 | Dedicated administrator to named guests, only approved management services; physical firewall and destination host policy apply. |
| FF-06 | Separate approved Tailscale client to APP1 TCP 443 only. Vendor grants, APP1 overlay policy and application roles enforce decrypted access; OPNsense sees the transport, not the full overlay policy. |
| FF-07 | Default disconnected. Exact update/activation/Tailscale dependencies require independently isolated, approved egress; include firewall-originated traffic. |
| FF-08 | Deny unlisted inter-zone traffic, ordinary-user management and protected destinations; also inspect same-zone/overlay host restrictions and matching logs/counters. |

No inbound forwarding, UPnP/NAT-PMP, subnet advertisements, exit node or public application sharing is included. A stale state can outlive a changed rule; inspect it read-only here. Only a separately approved correction may remove its exact state. Never flush all states or disable a firewall to obtain a result.

## Isolation and routing

**READ-ONLY - Proxmox host console, root or the approved sudo console session.** Inspect addresses, bridge membership, both route families and forwarding switches. No placeholders; these commands do not change settings:

```sh
ip -br address
bridge link
ip route
ip -6 route
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
```

Compare the output with **Dell node > System > Network** and the private map. Workload bridge members must provide their approved physical paths to HP, with no host IP or cross-zone route. Both forwarding values must be **0**. Inspect per-interface IPv6 behavior too; do not infer isolation from those two values alone.

- Trace cables and switch/bridge membership to exclude layer-2 contact with home/production. Review other administrator adapters, Wi-Fi, VPNs, Internet sharing and forwarding. Compare Windows network settings with local route/adapter inspection and the private map.
- Inspect **System > Routes > Status** in OPNsense and routes/forwarding at the Dell, guests and administrator station. Check automatic/default routes, policy routes, NAT and overlays as well as named rules. No route may bypass HP or reach protected assets.
- Inspect IPv4 and IPv6 separately: assigned addresses, router advertisements, DHCPv6, automatic routes and listeners. Baseline routed IPv6 stays disabled under the approved design; do not indiscriminately disable Windows IPv6 stacks. A routing/advertisement change needs C/D approval.
- In Beryl AX **INTERNET**, inspect Ethernet, Repeater, Tethering and Cellular. Upstream stays disconnected until an independent isolation design and rollback are approved. NAT or a lab router on a home LAN is insufficient. Tailscale and external updates depend on this gate.
- Review private protected IPv4/IPv6/overlay aliases and corporate public destinations, plus absence of home/production trust, federation, identity synchronization, credentials and data. Lab DNS/time must not fall back to corporate resolvers or forwarding.

Use configuration inspection and passive observations for real protected boundaries. Never send test traffic to home or production. A GUI screenshot, disconnected cable or static deny alias alone cannot establish complete FWT-01/FWT-02 success.

## Approved active checks

These checks generate traffic. They are separate from Phase 1 inspection and require approval naming the stage, lab-owned source/target, identity, one connection/service, expected result, evidence, stop condition and rollback. Use the complete [FWT-01](../../testing/TEST-PLAN.md#fwt-01---isolation-and-readiness) and [FWT-02](../../testing/TEST-PLAN.md#fwt-02---three-zone-network-and-administration) definitions and [Phase 5](../LAB-IMPLEMENTATION-GUIDE.md#phase-5-validation-and-final-submission) for the later bounded tools. Missing listeners or approval means NOT TESTED.

1. Establish a working allowed control to a known listening lab-owned service. Use only an approved lab-owned mock to represent the protected boundary; never a real protected address.
2. Make the single approved denied request. Check an unlisted inter-zone service and ordinary-user management denial within their separately named scopes. An approved administrator control and console observation must also succeed.
3. Match each result to the intended effective policy and private log/counter: **OPNsense > Firewall > Log Files > Live View** for routed traffic, the actual host policy for same-zone traffic, and vendor/APP1 rules for overlay traffic. A timeout, wrong password or stopped listener is insufficient.
4. Record source/target context, versions, approval/date, expected/actual result, policy/log reference, second observation and PASS/FAIL/NOT TESTED for every mandatory subcheck in **03 > Test Cases**. Reference **01 > Allowed Network Flows** and keep raw output private.

Complete HTTPS and overlay behavioral checks only when their approved services exist. Keep missing evidence visible and carry it to the owning later phase; do not infer a whole-test PASS from read-only inspection. [Acceptance criteria](../../testing/ACCEPTANCE-CRITERIA.md) require all mandatory subchecks and a separate owner UAT decision.

## Console recovery and rollback

For unexpected connectivity, stop the affected operation. Follow the approved console isolation plan to disconnect the external path, including wireless or USB alternatives; preserve private evidence. If access or mapping differs from the plan, obtain a bounded correction before continuing.

Before any separately approved B-D change, retain the current host network/firewall settings and a private password-protected HP configuration copy under **System > Configuration > Backups**. Verify file date, custody, recovery keys and the selected-release restore method. Confirm Dell/HP console access and the original Windows disk/data/service recovery plan. A guest snapshot is not a physical-firewall backup.

Use console to inspect interface/source, bridge/tag/PVID, rule order, host policy, NAT and the exact states. Restore only the approved saved settings within their recovery scope, then repeat the affected allowed/denied checks and second observation. Do not select another disk, reinstall, erase storage, disable protection or reconnect a home uplink as troubleshooting. Record the failure, correction and retest in **04 > Issue Log**.

## Version-dependent screens and editor

Match installed versions and switch revision to these primary references before use. Menu names below are inspection entry points, not permission to save/apply or migrate rules. If screens differ, stop for a reviewed equivalent.

- [Proxmox GUI](https://github.com/proxmox/pve-docs/blob/master/pve-gui.adoc), [bridges/VLANs](https://github.com/proxmox/pve-docs/blob/master/pve-network.adoc) and [firewall backend/automatic rules](https://github.com/proxmox/pve-docs/blob/master/pve-firewall.adoc).
- [OPNsense interfaces](https://docs.opnsense.org/manual/interfaces.html), [rules](https://docs.opnsense.org/manual/firewall.html), [routes](https://docs.opnsense.org/manual/routes.html) and [configuration backups](https://docs.opnsense.org/manual/backups.html). Interfaces use **Interfaces > Assignments**; modern and legacy rule screens differ. Inspect existing policy; do not run a migration.
- [TL-SG108E revision manuals](https://www.tp-link.com/us/support/download/tl-sg108e/) and [Beryl AX Internet modes](https://docs.gl-inet.com/router/en/4/user_guide/gl-mt3000/).
- [Windows inventory](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance), [network inspection](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipconfiguration) and [AD service dependencies](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/config-firewall-for-ad-domains-and-trusts).

Later guide procedures conditionally use Windows Server 2025 Desktop Experience, a supported domain-capable Windows 11, Ubuntu Server 24.04 LTS with Netplan/systemd-networkd, nftables and Apache 2.4, OpenSSL 3.x, Windows PowerShell 5.1 and an approved Tailscale client. Record actual builds, verified media/lawful terms and approved recovery in **01 > Virtual Machines** or **02 > Implementation Overview**. A different backend/version needs a reviewed equivalent; do not stack firewall managers or bypass Windows hardware requirements.

Where a later procedure says privileged editor, use an approved editor already present on that named Linux target. For the conditional **nano** example, assign **LabEditPath** privately to the exact approved file after saving its recovery copy.

**CONFIGURATION CHANGE - the later procedure's named Linux target, sudo/root, only its separately approved file and stage.** This is reference text, not part of Phase 1 inspection:

```sh
sudo nano "$LabEditPath"
```

Edit only the specified content; **Ctrl+O**, **Enter** saves and **Ctrl+X** exits. Reopen the file, check required owner/mode and run that procedure's syntax check before applying. Do not install an editor or save over an uncertain path.
