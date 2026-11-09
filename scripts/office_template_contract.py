"""Approved blank-template contract for the four-week lab; no lab execution.

The test plan owns the full methods, expected outcomes and second observations.
The checks below divide those methods into recordable steps, not new tests.
"""
import re

FILES = (
    "01-Lab-Environment-and-Architecture.xlsx",
    "02-Identity-and-Zero-Trust-Implementation.docx",
    "03-Security-Monitoring-and-Testing.xlsx",
    "04-Troubleshooting-and-Lessons.xlsx",
    "05-Final-Project-Submission.docx",
)
SHEETS = {
    FILES[0]: ("Hardware & Readiness", "Virtual Machines", "Network Zones", "Allowed Network Flows", "Resource Allocation"),
    FILES[2]: ("Security Events", "Denied Access Investigation", "Test Cases", "Requirements Coverage", "Automation Verification", "Backup & Restore", "Evidence Index", "Owner Acceptance"),
    FILES[3]: ("Issue Log",),
}
STATUSES = "NOT TESTED,IN PROGRESS,PASS,FAIL,BLOCKED,NOT APPLICABLE"
OWNER_DECISIONS = "PENDING,ACCEPTED,CHANGES REQUIRED"
ISSUE_STATUSES = "OPEN,IN PROGRESS,BLOCKED,RESOLVED"
RUBRIC = (
    ("Infrastructure and Network Security", 25),
    ("Identity and Access Controls", 25),
    ("Security Monitoring and Operations", 20),
    ("Testing and Recovery", 20),
    ("Documentation and Final Submission", 10),
)
WORD_SECTIONS = {
    FILES[1]: ("Implementation Overview", "Active Directory and User Roles", "Windows and Linux Endpoint Controls", "Application Accounts and Permissions", "HTTPS Certificate Configuration", "Six Application Access Tests", "Tailscale Remote Access", "Access Revocation", "Implementation Results and Limitations"),
    FILES[4]: ("Executive Summary", "Project Objectives", "Architecture Overview", "Implementation Summary", "Security Testing Results", "Key Findings", "Challenges and Lessons Learned", "Project Limitations", "Final Evaluation", "Supporting Deliverables and Evidence"),
}

# Each tuple is (recordable action, approved expected condition, owning detail).
# OVERALL rows quote the exact current plan; these children expose every check.
SUBCHECKS = {
    "FWT-01": (
        ("Inspect ownership, receipt, compatibility and physical hardware.", "Delivery estimates never count as receipt or validation.", "01 / Hardware & Readiness"),
        ("Inventory existing data/services and preserve the original Windows disk.", "No unapproved change to original data or services.", "01 / Hardware & Readiness"),
        ("Verify backup/console readiness and exact destructive approvals.", "Readiness and approval references recorded before dependent work.", "01 / Hardware & Readiness"),
        ("Inspect cables, bridge/NIC membership and other administrator adapters.", "No unapproved protected path or integration.", "01 / Network Zones"),
        ("Inspect routes, forwarding, IPv6 and private protected aliases.", "No unapproved protected path or integration.", "01 / Network Zones"),
        ("Inspect trust, synchronization, credentials and data boundaries.", "No home/production trust, sync, credential or data reuse.", "01 / Hardware & Readiness"),
        ("Inspect the disconnected or independently isolated approved egress.", "No unapproved protected path or integration.", "01 / Allowed Network Flows / FF-07"),
        ("Check a known listening lab mock; compare denial to policy log/counter.", "Mock connection denied by intended control. No actual protected asset receives traffic.", "01 / Allowed Network Flows / FF-08"),
        ("Compare inventory to physical/firmware view.", "Observed hardware agrees with the private inventory.", "01 / Hardware & Readiness"),
    ),
    "FWT-02": (
        ("Count the host, four baseline VMs and three named zones.", "One host; four VMs; Management, Corporate and Restricted.", "01 / Virtual Machines and Network Zones"),
        ("Compare allocations/reserves to measured capacity, including temporary restore space.", "Resource ledger fits actual capacity, including temporary restore space.", "01 / Resource Allocation"),
        ("Inspect FF-01 through FF-08 and automatic/state/NAT rules.", "Only approved source/service paths work.", "01 / Allowed Network Flows"),
        ("Demonstrate named administrator access and MFA where supported.", "Only approved source/service paths work; record MFA limits.", "01 / Allowed Network Flows / FF-01"),
        ("Verify physical console recovery separately.", "Console recovery remains available.", "01 / Hardware & Readiness"),
        ("Demonstrate WIN1 to APP1 HTTPS from an approved context.", "WIN1 to APP1 TCP 443 is permitted.", "01 / Allowed Network Flows / FF-03"),
        ("Demonstrate unlisted inter-zone listening-service denial using a working control.", "Default deny prevents extra access.", "01 / Allowed Network Flows / FF-08"),
        ("Demonstrate ordinary-user management denial with policy/log evidence.", "Ordinary-user management access is denied; missing credentials alone is insufficient.", "01 / Allowed Network Flows / FF-08"),
        ("Inspect same-zone DC host policy separately.", "Host policy constrains same-zone access.", "01 / Allowed Network Flows / FF-02"),
    ),
    "FWT-03": (
        ("Inspect ad.lab.test, DNS and Group Policy.", "Separate lab directory, lab DNS and effective policy.", "02 / Active Directory and User Roles"),
        ("Inspect ava/eli/uma, LabReaders/LabMaintainers/LabAdmins and separate privileged administrator.", "Three standard users, three role groups and one separate privileged administrator.", "02 / Active Directory and User Roles"),
        ("Verify standard WIN1 logon/name resolution and unintended privilege absence.", "Standard logon/DNS work; no unintended privileged membership.", "02 / Active Directory and User Roles"),
        ("C01: ava / LabReaders requests /reports/ with valid app credentials.", "Allow", "02 / Six Application Access Tests / C01"),
        ("C02: ava / no maintenance role requests /maintenance/ with valid app credentials.", "Deny", "02 / Six Application Access Tests / C02"),
        ("C03: eli / LabReaders requests /reports/ with valid app credentials.", "Allow", "02 / Six Application Access Tests / C03"),
        ("C04: eli / LabMaintainers requests /maintenance/ with valid app credentials.", "Allow", "02 / Six Application Access Tests / C04"),
        ("C05: uma / no reader role requests /reports/ with valid app credentials.", "Deny", "02 / Six Application Access Tests / C05"),
        ("C06: uma / no maintenance role requests /maintenance/ with valid app credentials.", "Deny", "02 / Six Application Access Tests / C06"),
        ("Compare manual app roles with approved AD roles and distinct password custody.", "App role mapping matches approved AD roles; no automatic synchronization.", "02 / Application Accounts and Permissions"),
        ("Remove eli from app LabMaintainers and the corresponding AD role; treat caches.", "Record exact changes and cache treatment; AD changes alone do not revoke app permission.", "02 / Access Revocation"),
        ("Retry the existing authenticated maintenance browser context.", "Revoked maintenance permission denies the existing context.", "02 / Access Revocation"),
        ("Retry a fresh authenticated maintenance request and compare elapsed time independently.", "Revoked maintenance permission denies the fresh context; record actual elapsed time.", "02 / Access Revocation"),
    ),
    "FWT-04": (
        ("Inspect supported Windows/Linux OS builds and recorded updates.", "Supported builds and recorded update status are in place.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect Windows antivirus and resultant policy.", "Baseline antivirus and effective policy are in place.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect both host firewalls.", "Baseline host firewalls are enabled and effective.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect standard/admin groups, single zone NIC and APP1 overlay exception.", "Separate privileges; no home/corporate profiles or bypass adapters.", "02 / Windows and Linux Endpoint Controls"),
        ("Attempt one harmless administrator-only action as a standard user.", "Standard users cannot administer hosts.", "02 / Windows and Linux Endpoint Controls"),
        ("Perform the approved administrator control.", "Authorized admin works.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect unnecessary listeners and forwarding.", "No unintended listener/forwarding bypass.", "02 / Windows and Linux Endpoint Controls"),
    ),
    "FWT-05": (
        ("Inspect one encrypted offline CA key/public root and one APP1 leaf.", "One CA/leaf; protected offline CA key; no private key in evidence.", "02 / HTTPS Certificate Configuration"),
        ("Inspect serverAuth/CA constraints and SAN app.ad.lab.test.", "Correct constraints and app.ad.lab.test hostname.", "02 / HTTPS Certificate Configuration"),
        ("Inspect current dates and remaining validity explicitly.", "Certificate dates are valid; record remaining validity without changing domain time.", "02 / HTTPS Certificate Configuration"),
        ("Inspect approved-client root trust and scope.", "No lab trust outside approved clients.", "02 / HTTPS Certificate Configuration"),
        ("Open the correct HTTPS name in an approved trusting lab browser.", "Correct chain/name/dates produce a normal HTTPS session.", "02 / HTTPS Certificate Configuration"),
        ("Use an otherwise functional untrusted lab client.", "Untrusted client rejects the chain; no warning bypass.", "02 / HTTPS Certificate Configuration"),
        ("Record the certificate-revocation-service exclusion.", "Certificate revocation services are excluded; report that limit.", "02 / Implementation Results and Limitations"),
    ),
    "FWT-06": (
        ("Inspect separate lab tailnet/identities, MFA/recovery and isolated-egress approval.", "No production tailnet, routes, identities or credentials.", "02 / Tailscale Remote Access"),
        ("Inspect APP1 and approved-client enrollment.", "Only the approved lab context is enrolled.", "02 / Tailscale Remote Access"),
        ("Inspect exact APP1 TCP 443 grant, additive policy and tag owners.", "Only app.ad.lab.test HTTPS is reachable by the approved context.", "02 / Tailscale Remote Access"),
        ("Inspect routes, exit node, public share, SSH, Funnel and Serve.", "No routes/exit node/public share/SSH/Funnel/Serve.", "02 / Tailscale Remote Access"),
        ("Inspect Linux overlay rules/forwarding, rule precedence and private DNS.", "Effective host/overlay policy restricts the single resource.", "02 / Tailscale Remote Access"),
        ("Demonstrate approved remote HTTPS with application roles.", "Approved remote HTTPS works with app roles.", "02 / Tailscale Remote Access"),
        ("Demonstrate unauthorized remote user denial.", "Wrong identity cannot access the resource.", "02 / Tailscale Remote Access"),
        ("Demonstrate wrong listening-port/resource denial with a working control.", "Wrong port/resource cannot be reached.", "02 / Tailscale Remote Access"),
        ("Remove the client grant/device authorization and inspect effective state.", "Authorization is revoked; record exact change/cache/state treatment.", "02 / Access Revocation"),
        ("Retry existing remote requests after revocation.", "Revoked client cannot access it through existing requests.", "02 / Access Revocation"),
        ("Retry new remote requests and record actual revocation times.", "Revoked client cannot access it through new requests; missing safe egress stays NOT TESTED.", "02 / Access Revocation"),
    ),
    "FWT-07": (
        ("Select two or three relevant sources and inspect access/rotation/time notes.", "Restricted logs/rotation; source/observer UTC/time differences recorded.", "03 / Security Events"),
        ("Verify DC1 account-logon auditing and relevant Kerberos records.", "Do not assume a WIN1 interactive event is recorded on DC1.", "03 / Security Events / E01-E02"),
        ("Record directory logon success.", "Attributable/searchable source record for directory success.", "03 / Security Events / E01"),
        ("Record one directory logon failure.", "Attributable/searchable source record for one failure.", "03 / Security Events / E02"),
        ("Record application allow.", "Attributable/searchable source record for app allow.", "03 / Security Events / E03"),
        ("Record authenticated application denial.", "Attributable/searchable source record for authenticated app denial.", "03 / Security Events / E04"),
        ("Record firewall denial.", "Attributable/searchable source record for firewall denial.", "03 / Security Events / E05"),
        ("Investigate one denial against a working control and intended rule/group.", "Explain who requested what, why denied and supporting evidence.", "03 / Denied Access Investigation"),
        ("Compare source/action/policy and preserve private originals.", "Five distinct event categories; no duplicate-request substitution.", "03 / Evidence Index"),
    ),
    "FWT-08": (
        ("Review one WIN1 PowerShell/Python local-capacity operation and approval.", "One approved read-only local query and private output.", "03 / Automation Verification / A01-A02"),
        ("Verify target/domain allowlist and private output path.", "WIN1/ad.lab.test target and reviewed private path only.", "03 / Automation Verification / A02"),
        ("Execute once and compare to the OS storage view.", "Intended summary is correct.", "03 / Automation Verification / A03"),
        ("Repeat the same approved operation.", "Repeat changes only intended output, never configuration/accounts/network.", "03 / Automation Verification / A04"),
        ("Safely check invalid target rejection.", "Invalid inputs fail safely.", "03 / Automation Verification / A05"),
        ("Safely check invalid path rejection.", "Invalid inputs fail safely.", "03 / Automation Verification / A06"),
        ("Compare before/after configuration and publication contents.", "No unintended changes; no credential/private inventory published; time/free-space may vary.", "03 / Automation Verification / A07"),
    ),
    "FWT-09": (
        ("Verify exact APP1 backup scope and approval.", "Pages/config/hashed app accounts/roles/server key/leaf/public root are covered.", "03 / Backup & Restore / B01"),
        ("Verify encryption, off-compute copy and recovery-key access.", "One encrypted off-compute backup; same-disk snapshots do not qualify.", "03 / Backup & Restore / B02"),
        ("Record backup age/time and manifest.", "Actual backup age/time and scope recorded.", "03 / Backup & Restore / B03"),
        ("Verify original off, approved unused temporary ID and disconnected copy.", "No overwrite of original/sole backup or duplicate live identities.", "03 / Backup & Restore / B04"),
        ("Keep copied Tailscale inactive before any isolated client attachment.", "No connected duplicate overlay identity.", "03 / Backup & Restore / B05"),
        ("Restore and measure restore-to-usable time with an independent clock.", "Actual scoped restore succeeds; no enterprise RPO/RTO threshold.", "03 / Backup & Restore / B06"),
        ("Compare hashes/content with the manifest.", "Restored data matches the declared manifest/content.", "03 / Backup & Restore / B07"),
        ("Check restored HTTPS through an isolated existing client.", "Restored HTTPS functions in isolation.", "03 / Backup & Restore / B08"),
        ("Check allowed and denied restored application roles.", "Restored authorization allows/denies the approved roles.", "03 / Backup & Restore / B09"),
        ("Record AD/CA/host exclusions and safe disconnected cleanup state.", "Recovery claims stay within APP1 scope; original and backup preserved.", "03 / Backup & Restore / B10"),
    ),
    "FWT-10": (
        ("Review every mandatory subcheck, control, evidence and defect.", "No missing mandatory evidence/unresolved safety issue.", "03 / Requirements Coverage and Evidence Index"),
        ("Review five final submission files, claims and the single rubric.", "Five final files present; claims supported; rubric totals 100.", "05 / Final Evaluation and Supporting Deliverables and Evidence"),
        ("Scan/review proposed public contents, metadata, staged diff and new history.", "Only reviewed sanitized artifacts/history are published.", "03 / Evidence Index"),
        ("Run finalized-report, links and Office validation.", "Required documentation/report checks pass.", "03 / Evidence Index"),
        ("Run PDF/rebuild, focused regression and whitespace checks.", "Required document checks pass; no Office/report PDFs generated.", "03 / Evidence Index"),
        ("Verify actual PR and exact final-head CI.", "Intentional publication is verified at the exact head.", "03 / Evidence Index"),
        ("Verify merge and live local/remote main equality.", "Observed merge and live synchronization recorded.", "03 / Evidence Index"),
        ("Record engineering verifier and evidence cutoff.", "Engineering record names actual verifier/cutoff.", "05 / Final Evaluation"),
        ("Record owner UAT separately, with explicit confirmation only when provided.", "Owner UAT stays PENDING without explicit confirmation.", "03 / Owner Acceptance"),
    ),
}


def approved_tests(plan: str) -> list[dict[str, str]]:
    """Read exact definitions from a plan, failing on omissions."""
    blocks = re.findall(r"^### (FWT-\d{2}) - ([^\n]+)\n(.*?)(?=^### |^## |\Z)", plan, re.M | re.S)
    result = []
    for tid, title, body in blocks:
        row = {"id": tid, "requirement": tid.replace("FWT", "FWR"), "title": title}
        for key, label in (("method", "Objective and method"), ("expected", "Expected result and pass/fail criteria"), ("second", "Second observation"), ("scope", "Scope")):
            match = re.search(r"^\*\*" + re.escape(label) + r":\*\* (.*?)(?=^\*\*|^\||\Z)", body, re.M | re.S)
            if not match:
                raise ValueError(f"{tid}: missing {label}")
            row[key] = match[1].strip()
        result.append(row)
    if [r["id"] for r in result] != list(SUBCHECKS):
        raise ValueError("Expected the ten approved FWT definitions in order")
    return result
