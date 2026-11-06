# Authoritative technical references

Research baseline: **2026-11-05 (America/Toronto)**. These are primary-source references for the proposed design, not a claim that referenced software is installed. Recheck supported versions, advisories, license/plan terms, commands, and hardware compatibility before each approved stage. Source fetch availability and version-specific ambiguity must be reported rather than guessed.

## Standards and namespaces

- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final) — resource-focused principles and logical architecture.
- [NIST SP 800-53 Revision 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) — security/privacy control catalog; use the current release material linked there.
- [NIST SP 800-53 Release 5.2.0 notice](https://csrc.nist.gov/News/2025/nist-releases-revision-to-sp-800-53-controls) — release baseline context, not a new revision number.
- [CIS Controls](https://www.cisecurity.org/controls) and [CIS Controls v8.1](https://www.cisecurity.org/controls/v8-1) — prioritized control areas; project mappings are tailored educational interpretations.
- [RFC 2606: Reserved Top Level DNS Names](https://www.rfc-editor.org/rfc/rfc2606) — `.test` for testing; no corporate domain required.
- [RFC 6761: Special-Use Domain Names](https://www.rfc-editor.org/rfc/rfc6761) — special-use name behavior and considerations.

## Proxmox

- [Official documentation downloads](https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation) — choose the version-matched administration guide at implementation time.
- [System requirements](https://www.proxmox.com/en/products/proxmox-virtual-environment/requirements) — virtualization and host requirements; supplied RAM does not establish compatibility.
- [Network configuration](https://pve.proxmox.com/wiki/Network_Configuration) — bridge/interface concepts; actual interface names must be inspected.
- [Installation and upgrade](https://pve.proxmox.com/wiki/Proxmox_VE_Installation_and_Upgrade) — supported installation paths and release-specific cautions.
- [Administration guide PDF](https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf) — management, firewall, backup, and recovery reference. Some Proxmox documentation endpoints restrict automated access; use the official download index if a direct fetch is refused.

## OPNsense

- [Virtual and cloud installation](https://docs.opnsense.org/manual/virtuals.html) — VM deployment entry point.
- [Firewall rules and processing](https://docs.opnsense.org/manual/firewall.html) — stateful policy, rule ordering, and default behavior.
- [Interface configuration](https://docs.opnsense.org/manual/interfaces.html) — interface assignment and private/bogon filtering implications.
- [Official documentation](https://docs.opnsense.org/) — current version-specific backup, logging, and hardening procedures.

## Windows evaluation and hardware

- [Windows Server 2025 Evaluation Center](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2025) — evaluation media, 180-day expiry, and stated initial activation requirement. Recheck terms and deadlines at use; no license entitlement or purchase is implied.
- [Windows Server hardware requirements](https://learn.microsoft.com/en-us/windows-server/get-started/hardware-requirements) — CPU, memory, and storage prerequisites; do not treat minimums as measured workload sizing.

## Readiness and network commands

- [Get-CimInstance](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance) — local read-only CIM inventory syntax used in Stage A.
- [Get-NetIPConfiguration](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipconfiguration) — local interface/DNS configuration inspection; output is private.

## Active Directory, DNS, and policy

- [Install Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/install-active-directory-domain-services--level-100-) — supported AD DS role installation and deployment workflow.
- [Install-WindowsFeature](https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature) — verified role-installation syntax; changes the approved target.
- [Install-ADDSForest](https://learn.microsoft.com/en-us/powershell/module/addsdeployment/install-addsforest) — verified new-forest/DNS syntax, secure DSRM prompt, reboot/functional-level considerations.
- [AD domain firewall requirements](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/config-firewall-for-ad-domains-and-trusts) — service dependencies and dynamic RPC scope; does not authorize production trust.
- [Core network components](https://learn.microsoft.com/en-us/windows-server/networking/core-network-guide/core-network-guide) — lab DNS/directory network deployment context.

## Endpoint and certificate verification

- [Test-ComputerSecureChannel](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-computersecurechannel) — member-machine secure-channel check; not a DC health test.
- [AD CS overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview) — PKI service components.
- [Certification Authority role](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certification-authority-role) — standalone/offline root and subordinate CA concepts.
- [Inspect certificates and stores](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/inspect-certificates-manage-certificate-stores) — verified certificate inspection and `certutil -verify -urlfetch` syntax; fetch URLs must be reviewed.
- [Certificate path validation and revocation policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/configure-certificate-path-validation-revocation-policy) — relying-party trust/revocation configuration; validation tools do not establish application behavior by themselves.

## Tailscale

- [Access control](https://tailscale.com/docs/features/access-control) — policy model and enforcement.
- [Default ACL and policy examples](https://tailscale.com/docs/reference/examples/acls) — initial allow-all warning; do not infer deny-all from missing policy.
- [Grant examples](https://tailscale.com/docs/reference/examples/grants) — explicit resource-scoped grants and additive access.
- [Device visibility](https://tailscale.com/docs/concepts/device-visibility) — identity/environment membership and default visibility concerns.
- [Exit nodes](https://tailscale.com/docs/features/exit-nodes) — capability deliberately excluded from this baseline.
- [Tailscale CLI](https://tailscale.com/docs/reference/tailscale-cli) — verify `tailscale status` against the installed version; output contains private identifiers.

## Twingate

- [Understanding connectors](https://www.twingate.com/docs/understanding-connectors) — outbound connector/resource model.
- [Resources](https://www.twingate.com/docs/resources) — exact resource addressing, DNS perspective, and explicit port restrictions; defaults require review.
- [Connectors](https://www.twingate.com/docs/connectors) — supported deployment methods; no token-bearing deployment command is copied into Git.
- [How firewalls work with Twingate](https://www.twingate.com/docs/firewalls-and-twingate) — resource scope, network controls, and audit considerations.
- [Connector connectivity troubleshooting](https://www.twingate.com/docs/connector-failures) — current outbound Controller/Relay dependencies; verify current protocols/ports rather than assume HTTPS alone is sufficient.

## Logging and automation

- [Windows Event Forwarding for detection](https://learn.microsoft.com/en-us/windows/security/operating-system-security/device-management/use-windows-event-forwarding-to-assist-in-intrusion-detection) — collection design and source coverage.
- [Source-initiated event subscriptions](https://learn.microsoft.com/en-us/windows/win32/wec/setting-up-a-source-initiated-subscription) — source permissions and subscription setup.
- [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) — verified `--since` and `--no-pager` inspection options; use the installed distribution's version.
- [Ansible check and diff modes](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html) — simulation/module limitations and sensitive diff output.
- [Ansible playbook CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-playbook.html) — syntax-check/check/diff/limit options; target inventory remains private.

## GitHub and repository workflow

- [GitHub Actions security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) — least privilege and full-commit pinning.
- [Official checkout action](https://github.com/actions/checkout) — bootstrap pins a full commit resolved from the official `v6` ref on the research date; stored checkout credentials are disabled.
- [GitHub CLI repository creation](https://cli.github.com/manual/gh_repo_create) — supported secure repository creation/public visibility workflow.
- [GitHub CLI authentication status](https://cli.github.com/manual/gh_auth_status) — inspect existing supported authentication without exposing a token.

The offline architecture makes no claim about Google Wifi VLAN capabilities and requires no home-network change. Hardware/network capability verification belongs to the separately approved readiness stage.

## Command verification limits

Proposed Stage A/E/F/G/I/J/L examples use syntax confirmed in the corresponding primary documentation. They were not run on lab assets. Installation details, firewall backend/rules, Linux distribution commands, recovery commands, software versions, provider plan features, and actual target values intentionally require a version-specific reviewed change record before execution. Python/Git repository checks are verified locally during Task 001.
