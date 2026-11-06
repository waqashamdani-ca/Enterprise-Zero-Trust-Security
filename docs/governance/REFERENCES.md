# Authoritative technical references

Research update: **2026-11-06, America/Toronto, T6**. Primary guidance supports the focused four-week specification; it does not establish installed versions or executed commands. Recheck compatibility, advisories, lawful terms and installed help at stage entry. No software/provider subscription is purchased by T6.

## Standards and namespaces

- [NIST SP 800-207](https://csrc.nist.gov/pubs/sp/800/207/final): resource-focused principles; no compliance certification.
- [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606): .test is reserved for testing.
- Earlier detailed NIST/CIS mappings remain historical context in Git; they are not additional evidence requirements.

## Proxmox

- [Official documentation](https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation) and [administration guide](https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf): select the installed release.
- [Official network source](https://github.com/proxmox/pve-docs/blob/master/pve-network.adoc) and [installation source](https://github.com/proxmox/pve-docs/blob/master/pve-installation.adoc): bridges and installer/disk cautions.
- Direct admin-guide HTML returned 403 during T6 research; official source/download references were used. No installed-backend or disk command was verified on a host.

## OPNsense

- [Virtual installation](https://docs.opnsense.org/manual/virtuals.html): VM deployment.
- [Firewall processing](https://docs.opnsense.org/manual/firewall.html): incoming/stateful policy and automatic/floating/group/interface order; quick and non-quick behavior differ.
- [Firewall logging](https://docs.opnsense.org/manual/logging_firewall.html): log/counter interpretation and existing-state limits.
- [Interfaces](https://docs.opnsense.org/manual/interfaces.html): exact NIC assignment, private/bogon settings.

## Windows evaluation and hardware

- [Windows Server Evaluation](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2025) and [hardware requirements](https://learn.microsoft.com/en-us/windows-server/get-started/hardware-requirements): check lawful terms, activation/expiry and selected version requirements.
- [Dell Precision 5820 manuals](https://www.dell.com/support/product-details/en-us/product/precision-5820-workstation/docs): match exact chassis, firmware, cooler, processor, storage/adapter and slot before approval. T6 does not certify the ordered parts' fit.
- The latest owner procurement plan/receipt records remain private. Public documents record order status and expected dates only, not serials, order IDs or real inventory addresses.

## Readiness and network commands

- [Get-CimInstance](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance) and [Get-NetIPConfiguration](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipconfiguration): proposed read-only local readiness examples; outputs stay private.

## Active Directory, DNS, and policy

- [AD DS deployment](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/install-active-directory-domain-services--level-100-), [Install-WindowsFeature](https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature) and [Install-ADDSForest](https://learn.microsoft.com/en-us/powershell/module/addsdeployment/install-addsforest): lab-only installation, secure prompt and reboot considerations.
- [AD firewall requirements](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/config-firewall-for-ad-domains-and-trusts): scope required services to approved lab systems. Same-zone host rules still matter.

## Endpoint and certificate verification

- [Test-ComputerSecureChannel](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-computersecurechannel?view=powershell-5.1): supported member-machine check, not DC health. Initial direct fetch failed; Microsoft indexed documentation confirmed syntax. Verify locally installed help before use.
- [OpenSSL req](https://docs.openssl.org/3.5/man1/openssl-req/), [x509](https://docs.openssl.org/3.5/man1/openssl-x509/) and [verify](https://docs.openssl.org/3.5/man1/openssl-verify/): one CA, one leaf, extensions, chain/name/date checks. Commands target OpenSSL 3.x and must match installed help.
- [Apache TLS module](https://httpd.apache.org/docs/2.4/mod/mod_ssl.html): certificate/key and protocol directives. No AD CS/separate issuer or certificate-revocation infrastructure is required.

## Application authentication and authorization

- [Apache authentication guide](https://httpd.apache.org/docs/2.4/howto/auth.html), [file groups](https://httpd.apache.org/docs/2.4/mod/mod_authz_groupfile.html), [authorization merge behavior](https://httpd.apache.org/docs/2.4/mod/mod_authz_core.html) and [htpasswd](https://httpd.apache.org/docs/2.4/programs/htpasswd.html): local hashed accounts, group-protected directories, AuthMerging and interactive passwords.
- [Apache control wrapper](https://httpd.apache.org/docs/2.4/programs/apachectl.html): configtest; package activation/path wrappers differ.
- File-based roles are manually mapped to AD groups; these references do not establish AD SSO or synchronization.

## Tailscale

- [Access control](https://tailscale.com/docs/features/access-control), [grant syntax](https://tailscale.com/docs/reference/syntax/grants) and [grant examples](https://tailscale.com/docs/reference/examples/grants): explicit additive policy, exact destination and TCP 443.
- [ACL examples](https://tailscale.com/docs/reference/examples/acls): review permissive initial/default policy; omitted content is not proof of deny-all.
- [CLI reference](https://tailscale.com/docs/reference/tailscale-cli): proposed status inspection, private output.
- [Device removal](https://tailscale.com/docs/features/access-control/device-management/how-to/remove): verify current revoke/remove behavior and actual existing/new session denial.
- Recheck current plan/MFA/logging/identity terms at stage entry. No production tailnet, subnet routing, exit node, public sharing or remote management service is included.

## Twingate

Historical navigation anchor only. Twingate is excluded from the T6 baseline; no second provider, connector or comparison is required. Earlier references remain in Git history.

## Logging and automation

- [Kerberos authentication auditing](https://learn.microsoft.com/windows/security/threat-protection/auditing/audit-kerberos-authentication-service): confirm which host emits the actual directory authentication events.
- [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html): read-only --since/--no-pager examples. Apache request logs are separate.
- Existing PowerShell/Python supports one local capacity-summary operation. T6 adds no executable lab automation, Ansible requirement, collector VM or SIEM.

## GitHub and repository workflow

- [Actions security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) and [official checkout](https://github.com/actions/checkout): least privilege, full commit pin, no retained checkout credentials.
- [GitHub CLI authentication](https://cli.github.com/manual/gh_auth_status): existing secure authentication; never expose tokens.
- Current [build instructions](DOCUMENTATION-BUILD.md) define offline document/PDF checks.

## Command verification limits

T6 reviewed primary vendor descriptions/syntax for proposed inventory, AD deployment, member checks, OpenSSL, Apache, Tailscale and journal examples. It executed none on lab assets. Installed versions/backends, actual paths, compatibility, activation, provider behavior, recovery targets and Linux package commands require a future approved change record. Documentation CI fetches no external references and reaches no lab systems.
