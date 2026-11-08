# Backup and recovery reference

Use with [Phase 4](../LAB-IMPLEMENTATION-GUIDE.md#d-back-up-app1-and-restore-it-in-isolation) for FWR-09/FWT-09. Demonstrate recoverability with exactly one encrypted off-compute APP1 backup and one temporary isolated restore. Preserve the original VM and sole archive. These are proposed instructions; an actual restore, measured time, data/HTTPS/role evidence and second observations are required before PASS.

The explicit L recovery approval must cover assets, private values, permitted changes, validation, stop/rollback and cleanup. E/H/I approval also covers any directory/application/remote final-state changes; relevant C/D/F scopes cover exact client/network/firewall changes. Documentation approval supplies none of those implementation approvals. Use existing Dell/Proxmox, physical HP/OPNsense, switch and WIN1; add no permanent VM, zone or recovery product.

## Required private recovery plan

**Operational procedure: BLOCKED pending private design.** The public architecture does not identify actual port/NIC/bridge/VLAN mappings or an owner-selected encrypted storage backend. Do not start this drill or attach a restored NIC until both prerequisites below are reviewed and approved. FWT-09 and dependent unexecuted subchecks remain NOT TESTED.

| Required record | What the owner-approved plan must identify |
| --- | --- |
| Encrypted storage | Exact external device/backend, existing encryption, supported unlock/mount/unmount/lock procedure, capacity, mount path/storage ID and separate recovery-key custody/check. No formatting or new encryption product is approved here. |
| Existing isolated path | Actual existing WIN1-to-physical-HP-to-restored-APP1 path; switch ports, physical HP assignments, Dell NIC/bridge/tag membership, other attachments and both address families. Include the exact disconnect/verify/reconnect checklist, client address/name mapping, narrow rules, protected console access and rollback. |
| VM/archive identity | Original APP1 ID/disks; an approved different unused temporary VM ID and disk storage; restore allowance; exact archive/time/coverage; no overwrite; no autostart/HA/start automation for the copy. |
| Guest/evidence state | Approved final role/remote state, manifest paths/custody, expected hashes/content and HTTPS decisions, independent observer clock, stop point and private evidence locations. |
| Recovery/cleanup | Exact client/HP/host settings saved before changes, original-off sequence, copied-overlay disablement, safe removal or retention of the disconnected copy, encrypted-media detachment and original/final-state verification. |

The intended logical test path includes **WIN1 -> physical HP OPNsense -> restored APP1**. This is an enforcement requirement, **not a verified physical connection recipe**. A shared trunk, management attachment, switch port or extra adapter can defeat isolation. No fixed bridge, VLAN, NIC or port mapping is inferred. A disconnect instruction for a virtual firewall cannot isolate the HP appliance.

If the existing approved attachments cannot realize that path while excluding every home/production/ordinary-lab/overlay path, stop for a separately reviewed design. Do not create a bridge/VLAN/NIC, move switch ports, bypass the physical firewall or treat an unverified segment as isolated. Keep original APP1 and the sole backup preserved throughout a failed drill.

## Supported encrypted storage options

Proxmox's [Directory backend](https://github.com/proxmox/pve-docs/blob/master/pve-storage-dir.adoc) can use a mounted external filesystem; it does not itself encrypt backup archives. This procedure conditionally uses an **already approved encrypted external volume** with a supported Linux mount and owner-approved recovery procedure. The encrypted device must be physically separate from Dell's compute/guest disks, and be safely locked/detached after the drill. Plain compression, a local snapshot or a same-disk archive is not an encrypted off-compute copy.

An already approved Proxmox Backup Server backend supports [client-side encrypted backups](https://pbs.proxmox.com/docs/backup-client.html#encryption). It is a different storage/restore/key-custody procedure. Adding that product/server/network path is outside this three-VM design and is not prescribed here; an owner decision and separately reviewed backend-specific procedure would be required. Do not apply the Directory commands to it or silently substitute unencrypted storage.

The owner must select and verify the backend before operation. No disk-format, encryption-installation, partitioning or key-generation command is included. Unlock secrets and recovery keys are never command arguments, public files, screenshots or stored beside the backup. A mounted filesystem or label alone does not establish encryption; compare the full device/encryption chain and prove approved recovery-key access without exposing it.

## Final authorization state

Before backup, decide whether the final lab remains revoked after Phase 3 or returns to normal analyst/engineer/remote workflows. Under explicit existing E/H/I scope only, normal handover may restore eli to **both** AD and application **LabMaintainers**, and separately re-enroll/re-authorize only the exact approved remote client with its narrow APP1 TCP 443 grant. Keep distinct credentials, existing reader membership and all other denials.

Record each approved change, actual device/address review and affected permit/deny retest in **02 > Access Revocation / Tailscale Remote Access** and **03 > Test Cases** before taking the backup. If restoration is not approved, preserve the revoked state and report the unavailable workflow; do not claim normal engineer/remote acceptance. The recovery role checks use ava and hold in either approved eli state. Never restore permission merely to obtain a PASS.

## APP1 manifest and private custody

**Target / approval:** original APP1 Proxmox console, root, L recovery scope; existing conditional Ubuntu profile. Record selected versions and actual file paths first. Preserve older manifests and configuration copies. This manifest is private recovery material, including paths and hashes, not a public artifact.

Declare and inspect synthetic pages **/srv/labapp**, active Apache configuration **/etc/apache2**, **/etc/labapp** including users/groups, **app.key**, **app.crt**, **lab-ca.crt**, and required guest networking/firewall/time configuration. Confirm effective Apache includes and symlink targets are covered by declared paths and included guest disks. Root access must read every declared file; resolve missing/profile-different paths before backup, never silently exclude them.

Inspect **/root/APP1-manifest.sha256** before creation; it must be a new unused path, not a symlink. If it already exists, stop and review a new unique private filename instead of overwriting it. Keep permissions owner-only. The retained command below writes that one manifest and otherwise reads declared files.

**CONFIGURATION CHANGE to one private manifest, otherwise READ-ONLY - original APP1 console, root shell, L approval.** Use only after the unused-path and coverage checks; no file content is printed:

```sh
sudo -i
umask 077
LabManifestPath=/root/APP1-manifest.sha256
find /srv/labapp /etc/apache2 /etc/labapp /etc/netplan /etc/nftables.conf /etc/systemd/timesyncd.conf.d -type f -exec sha256sum -- {} + > "$LabManifestPath"
```

**Check:** no find/read errors, nonempty output, every declared file and required TLS/role/page/config file has an entry. `find -type f` does not follow external symlink targets; missing coverage requires a reviewed scope/profile correction before proceeding. Verify owner-only custody and copy the original manifest through the approved private media path to separate protected storage **before backup**. Retain its hash/identity independently so a later changed manifest cannot validate a changed restore. Never publish manifest, keys, credentials or password hashes.

## External mount and backup storage

**Target / approval:** Proxmox host console/root and Datacenter storage GUI, exact L-approved external device and Directory entry. Save existing storage configuration privately. Keep console access; no mount/unlock command is guessed for the missing backend.

1. Unlock/mount the already encrypted external device using only its approved backend procedure. Compare actual device identity, encryption chain, exact mountpoint and available capacity with the private plan. Verify separate recovery-key access using the approved check; do not display/copy the key into logs or store it on the media.
2. At **Datacenter > Storage**, inspect the reviewed existing Directory entry. Only if approved and unused, **Add > Directory**: **ID lab-backup**, exact externally mounted encrypted path, **Content VZDump backup file**, intended Dell node only. Do not use the host's ordinary directory or guest-disk storage. No scheduled job, prune/delete policy or extra backup is introduced.
3. Set **LabBackupMountPath** privately in the host shell to that entry's exact external mountpoint. The conditional **lab-backup** commands below apply only when that ID and Directory type were approved. An existing different ID needs its reviewed equivalent; do not change another storage.

**CONFIGURATION CHANGE followed by READ-ONLY - Proxmox console/root, approved lab-backup Directory entry only.** The guard marks storage offline when its mount is absent; it does not mount, format or encrypt anything:

```sh
pvesm set lab-backup --is_mountpoint 1
findmnt --mountpoint "$LabBackupMountPath"
lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINTS
pvesm status
```

**Check:** **findmnt --mountpoint** identifies the exact mounted external target, not the host filesystem underneath; **lsblk** and the backend record identify its external encrypted device chain. **pvesm status** shows active storage with sufficient space. Independently inspect **/etc/pve/storage.cfg** for the exact path/content/node and **is_mountpoint** guard. The [pvesm reference](https://github.com/proxmox/pve-docs/blob/master/generated/pvesm.1-synopsis.adoc) defines this option; `1` is the boolean shorthand for guarding the configured path. If the Directory path is not the actual mountpoint, stop for a reviewed exact-mount configuration instead of applying this shorthand blindly.

For available capacity, compare storage **Summary** with the selected device's available bytes and the full APP1 disk/temporary-restore allowance. The mount guard does not prove encryption, validate the correct device or protect against a wrong mounted filesystem; those are separate checks. Missing/wrong mount, unverified encryption/key access or insufficient capacity blocks backup. Never test fallback by writing to the unmounted host directory, and never delete the sole archive to free space.

## Backup archive and original-off sequence

**Target / approval:** original APP1 console and Proxmox GUI, L recovery approval. Have the protected original manifest, selected final authorization state and reviewed external storage. No infrastructure operation follows from this documentation task.

1. Inspect APP1 **Hardware** and **Options**. Match the original ID, included guest disks and configuration to the declaration; no declared data may live on an omitted disk or outside the VM. Inspect any per-disk backup exclusion, hooks and automatic restart/HA/jobs. Stop if an automation could restart the original during the drill; any correction needs its exact approval.
2. Cleanly shut down original APP1 from the guest console. Confirm **Stopped** before backup and retain it off for the whole restore test. A Stop-mode backup of a previously running guest can resume it; do not rely on selecting Stop alone.
3. Select **APP1 > Backup > Backup now**. Recheck original ID, approved encrypted external storage, **Mode Stop**, selected supported compression and no unrelated retention/delete action. Start exactly one full APP1 backup. Inspect completion/task output for errors, archive identity/date/size and every included disk; preserve the task log privately. A stopped-guest backup can briefly show a QEMU read process without booting the guest; confirm final stopped state independently.
4. In storage **Backups**, identify that exact archive and protect it through the selected release's supported protection/retention controls and private custody. No later task/cleanup may overwrite or prune it. Record backup time/age and protected manifest reference in **03 > Backup & Restore**, B01-B03. Archive existence or a successful backup job alone does not prove recovery.

[Proxmox backup/restore](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc) explains full backup and stop/live-restore behavior. Compression is not encryption. A physical HP configuration backup, AD/CA/Proxmox recovery and any broader disaster recovery are separate scopes; this archive is not their substitute.

## Restore a disconnected copy

**Target / approval:** Proxmox GUI/console, approved unused temporary APP1 ID and reviewed guest-disk storage; L recovery scope. The original remains stopped and no duplicate identity is connected.

1. Recheck the temporary ID is unused and differs from original APP1. Confirm sufficient space/reserves, archive identity/coverage and correct target storage. Preserve the original VM/disks and sole archive. Do not select overwrite/force, the original ID or a replacement disk operation.
2. From storage **Backups**, select the exact APP1 archive > **Restore**. Keep **Start after restore** and **Live restore** off. Start an independent observer clock **immediately before confirming Restore**; retain actual UTC start separately from guest time.
3. Inspect completed restore output for the new ID/disks. **Before any start**, open copy **Hardware > Network Device > Edit > Advanced > Disconnect** for every NIC. Set **Options > Start at boot: No** and inspect no HA/job/start automation can start it. Compare NIC state independently with the host configuration/private checklist. Do not assume the archived startup/network options are safe.
4. Reconfirm original **Stopped**, every copy NIC disconnected and no automatic start. Boot only the copy via its **Console**, without a client attachment. Use the copied-overlay and integrity checks next. If any state is unclear, stop and keep the copy disconnected.

## Copied Tailscale and integrity check

**CONFIGURATION CHANGE - restored APP1 copy's console only, sudo/root, L approval; conditional Ubuntu/systemd profile.** Stop/disable copied overlay before any connection. Never run this on the original:

```sh
sudo systemctl disable --now tailscaled
sudo systemctl is-active tailscaled
```

**Check:** inactive, with a normally nonzero is-active exit. Also inspect persistent disabled state; stopped alone does not establish disabled. Keep all Proxmox NICs disconnected during these checks. For another service/backend obtain its reviewed equivalent; do not enroll, log in, advertise routes or reuse the copied identity online.

**READ-ONLY - disconnected restored APP1 copy console, sudo/root, same selected profile.** Verify startup disabled separately from current inactivity:

```sh
sudo systemctl is-enabled tailscaled
```

**Check:** **disabled** (or an explicitly reviewed more restrictive state), normally nonzero. An enabled/active or uncertain service blocks connection. Compare service/unit details if an alias or another startup mechanism exists; preserve failure evidence.

Transfer the independently retained original manifest through the approved private **offline** media/comparison path, not an improvised network connection. Set **LabOriginalManifestPath** privately to that verified original file. Check all declared files **before** temporary firewall/name/network changes. Also inspect expected synthetic page content, owner/modes and absence of missing included paths; hashes alone do not prove runtime behavior.

**READ-ONLY - restored APP1 copy console, root for protected files.** Compare the declared original hashes without rewriting any file:

```sh
sha256sum -c "$LabOriginalManifestPath"
```

**Check:** every declared file reports **OK**, using the authentic separately retained manifest. A mismatch/missing file/read error is FAIL; preserve the failed output and investigate archive/coverage. Never regenerate the manifest from the copy to turn a mismatch into PASS. Record B04-B07 and private evidence; do not print key/password-file contents.

## Physical-firewall isolated test path

**Connection gate: BLOCKED until the exact private plan is supplied.** No safe attachment sequence can be derived from unspecified HP/switch/Dell links. The following are acceptance conditions for that future existing-path checklist, not a claim that a topology has been verified.

1. At consoles, verify original APP1 stays off; the restored copy is the only APP1 identity that could run. Keep its NICs disconnected, autostart off and copied Tailscale inactive/disabled. Save WIN1's actual adapter/hosts/address/route state and the exact HP/guest firewall settings before approved temporary changes.
2. The private checklist must physically/logically exclude every nonparticipant attachment: home/production, upstream/Beryl paths, other lab guests, extra switch/bridge members and alternate client Wi-Fi/VPN/overlay/forwarding/IPv6 paths. Preserve only the separately reviewed protected console/administration recovery. Inspect shared/trunk tagged and untagged membership, addresses/routes/advertisements and actual port assignments; a disconnected uplink alone is insufficient.
3. Retain the **physical HP firewall on the routed test path** between the existing WIN1 and restored APP1 attachments. Do not connect them directly on a shared bridge to bypass it. Do not create a new permanent VM/zone, new bridge/VLAN/NIC or unapproved Proxmox/OPNsense/switch mapping. If these conditions cannot be met with approved existing paths, leave operation blocked for design approval.
4. Apply only the approved temporary WIN1 address/name settings through console/local editor. Save **C:\Windows\System32\drivers\etc\hosts** before a single private mapping **LAB_RESTORE_APP_IP app.ad.lab.test**; the actual restored address/mask and any exact lab-only next hop come from the private plan. Do not invent a gateway, borrow a corporate resolver or add a second NIC. Preserve WIN1's approved public lab-root trust. No AD/DNS/Internet service is required for local app credentials; if the existing client cannot sign in safely offline, obtain its approved access method first.
5. On HP, the separately approved temporary **ingress** rule permits only **LAB_RESTORE_CLIENT_IP -> LAB_RESTORE_APP_IP, TCP 443**, with logging, through the specified existing test interface. Inspect effective floating/group/automatic rules, state and default denies; no all-host/subnet/any-port permit, NAT, new egress or protected-network route follows. Record only the named temporary rule and exact rollback; do not disturb ordinary policy or flush all states.
6. On the still disconnected **copy only**, preserve its boot file/full active rules. If the private test client differs from the saved exact HTTPS sources, add only **ip saddr LAB_RESTORE_CLIENT_IP tcp dport 443 counter accept** through [scoped atomic replacement](03-Linux-Network-and-Host-Policy.md#scoped-atomic-replacement). Put it after the physical-source HTTPS permit and before the input chain closes; retain the earlier tailscale0 drop, forward drop and unrelated tables. Record this deliberate post-integrity-check difference. Never edit the original or broaden to a subnet.
7. Verify the complete private checklist, saved narrow rules, both route families/forwarding, actual disconnected/nonparticipant states and console recovery using separate configuration/passive observations. Only then may the exact restored NIC and one existing WIN1 path be connected as approved. No live original, copied overlay, home/production attachment or physical firewall bypass may exist. Unexpected connectivity means stop and disconnect using the approved console plan; never probe a protected address to prove isolation.

Record the approved map/checklist reference, observations and temporary differences privately in **03 > Backup & Restore / Evidence Index**. Without every dependency, connection/function/time subchecks stay NOT TESTED. A conceptual diagram, rule screenshot or documentation CI pass supplies no safe operational topology.

## HTTPS role checks and recovery time

**Targets / approval:** existing isolated WIN1 browser, restored APP1 console and physical HP policy/log view, approved L/H/D/F test scope. Original stays off; copied Tailscale stays disabled; no external connectivity. Keep the independent observer clock running from the restore confirmation, including setup and all usability checks.

1. On the copy, inspect **apache2** service/configuration/listener using [the retained Apache checks](04-HTTPS-and-Application-Roles.md#apache-https-and-group-authorization); do not install or widen services. At WIN1 verify the actual browser connection address maps **app.ad.lab.test** to this restored copy. Use the already approved public root and current real time; no warning bypass or domain-clock change.
2. In a clean browser context use valid **ava application** credentials to open **https://app.ad.lab.test/reports/**. Expect normal trusted HTTPS, synthetic report and HTTP 200. Compare Apache user/path/status and HP's exact routed permit to the effective host policy. This is the working allowed control.
3. Make a new server request for **https://app.ad.lab.test/maintenance/** with valid ava credentials. Expect authenticated HTTP 403, matching group/authorization/access/error evidence and no maintenance access. HTTP 401, broken DNS, TLS error or stopped service is not this denial. Ava's decisions remain the same whether eli is restored or revoked.
4. Stop the independent observer clock **only when** declared file integrity/content and usable HTTPS allow/deny checks have passed. Record actual UTC start/end, elapsed time, observer identity/resolution and any setup/delay/failure/retry interval. If checks cannot finish, record elapsed-to-stop and the failure; do not call it successful recovery or fabricate a number.

Use **03 > Backup & Restore**, B06 actual restore-to-usable time, B07 integrity/content, B08 HTTPS and B09 roles, with task/clock/hash/log/policy second observations; link FWT-09.06-.09 in **Test Cases**. These are separate observations by the operator, not independent human review. This measures the scoped APP1 exercise only, with no enterprise recovery-time/recovery-point target or AD/CA/host/physical-firewall disaster-recovery claim.

## Cleanup, rollback and off-compute custody

**Targets / approval:** restored-copy console, Proxmox, isolated WIN1, physical HP and encrypted media, exact L cleanup/rollback scope. Preserve all failure/task/time/integrity/function evidence privately before cleanup.

1. Disconnect every restored NIC first, then cleanly shut down the copy and confirm **Stopped**. Confirm autostart/HA/start jobs cannot reconnect it and copied Tailscale remains disabled. Original APP1 must stay off until the duplicate cannot run/connect. Never delete original APP1/disks or the sole backup.
2. Restore WIN1's saved adapter/address/routes/hosts state and remove only the named HP temporary rule/state and copied-host exception through their approved recovery methods. Verify actual settings against the before-state before original startup; preserve unrelated rules/tables and console recovery. Reconnect original lab attachments only in the private checklist's approved order after copy isolation is established. No guessed firewall-NIC reattachment or global state flush.
3. Delete the temporary copy/disks only if approval identifies that exact unused temporary ID and cleanup scope. Recheck ID and original/archive identity before confirmation. Otherwise retain it stopped, disconnected, autostart off with restricted custody; do not describe retained resources as deleted. Record actual final disposition.
4. Resume original APP1 only after the disconnected-copy checks. Verify its unchanged files/configuration, expected HTTPS/ava roles, intended eli AD/app state and exact approved remote/grant/device state. Any re-enrollment/permission restoration needs E/H/I authority and affected retests; do not silently restore access. If verification fails preserve the failure and recover only approved saved settings at console.
5. Ensure no backup/restore task uses the external storage. Safely unmount, lock and detach it using the approved selected-backend sequence; prevent subsequent fallback jobs/writes and verify absent mount/offline guarded storage. Store encrypted media away from compute with readable private recovery instructions; keep the recovery key separately protected. Never replace it with an unencrypted convenience copy.

Record **03 > Backup & Restore**, B10 cleanup/final state/exclusions; B01-B03 archive identity, custody, encryption/key access and actual age/time; **Evidence Index** for private originals; **04 > Issue Log** for failures/remediation. Confirm all ten FWT-09 mandatory subchecks have actual evidence before overall PASS. No restore, native test, owner acceptance or independent human sign-off is supplied by these instructions.

If any stage fails, stop the affected work, leave the restored copy disconnected and original/sole backup preserved, and record the actual failed step. Inspect key/mount access, archive coverage, space, copied-service state, hashes and intended isolated policy/service. Do not overwrite the original/only archive, reconnect broadly, install encryption ad hoc or change the expected result. Resume only after the exact missing prerequisite/correction and rollback are approved.

## Version-specific verification

Record Proxmox VE/guest builds. Match storage, restore/start and protection choices to local **pvesm** help and vendor [Directory](https://github.com/proxmox/pve-docs/blob/master/pve-storage-dir.adoc), [pvesm](https://github.com/proxmox/pve-docs/blob/master/generated/pvesm.1-synopsis.adoc), [networking](https://github.com/proxmox/pve-docs/blob/master/pve-network.adoc) and [backup/restore](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc) guidance before execution.

Guest commands assume existing Ubuntu Server 24.04 LTS/systemd/nftables/Apache 2.4 and **/etc/labapp**. Verify [findmnt --mountpoint](https://manpages.ubuntu.com/manpages/noble/man8/findmnt.8.html) against host util-linux and [systemctl](https://manpages.ubuntu.com/manpages/noble/man1/systemctl.1.html) against the guest. Startup disablement alone leaves active services running: retain **disable --now** and independent inactive/disabled checks. Different options/backends/startup mechanisms require reviewed equivalents; never install tools or change topology to match this reference.
