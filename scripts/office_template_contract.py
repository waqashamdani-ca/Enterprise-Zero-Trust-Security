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
# Office 03 released recording fields in the existing table order.
OFFICE03_TABLES = {
    "Security Events": ("A7:K12", (
        "Event ID", "Planned category", "Planned source / check", "Actual source and action", "Source UTC", "Observer UTC",
        "Time difference notes", "Actual record summary", "Log access and rotation", "Status", "Evidence reference",
    )),
    "Denied Access Investigation": ("A7:G14", (
        "Field ID", "Investigation prompt", "Actual observation", "Second observation",
        "Status", "Evidence reference", "Defect reference",
    )),
    "Test Cases": ("A7:L108", (
        "Test ID", "Requirement ID", "Check ID", "Test objective and method", "Expected result", "Second observation / owning detail",
        "Status", "Actual result", "Evidence reference", "Defect reference", "Retest result", "Operator / date / version",
    )),
    "Requirements Coverage": ("A7:I17", (
        "Requirement ID", "Approved required result", "Security control", "Test ID", "Acceptance criterion",
        "Owning deliverable", "Engineering status", "Evidence reference", "Defect reference",
    )),
    "Automation Verification": ("A7:G14", (
        "Check ID", "Verification prompt", "Actual result", "Second observation",
        "Status", "Evidence reference", "Defect reference",
    )),
    "Backup & Restore": ("A7:G17", (
        "Check ID", "Recovery prompt", "Actual result", "Second observation",
        "Status", "Evidence reference", "Defect reference",
    )),
    "Evidence Index": ("A7:G13", (
        "Evidence ID", "Requirement / check ID", "Description", "Private original reference",
        "Reviewed public reference", "Reviewer / review date", "Redaction and limitations",
    )),
    "Owner Acceptance": ("A7:G12", (
        "UAT item", "Workflow for owner review", "Owner decision", "Owner reviewer / date",
        "Actual usability observation", "Limits and follow-up", "Explicit confirmation reference",
    )),
}
OFFICE04_TABLE = ("Lab04Table1", "A7:K13", (
    "Issue ID", "Date", "Affected component / check", "Problem", "Impact", "Cause or investigation",
    "Corrective action", "Verification / retest", "Status", "Lesson learned", "Evidence reference",
))
OFFICE04_LINKS = {"F2": "'Test Cases'!A7", "I2": "'Evidence Index'!A7"}
OFFICE04_PROMPTS = {
    "C3": ("unique Issue ID", "observed and expected results", "effect and severity", "FWT-01 to FWT-10",
           "FWR, FSC and FAC", "FF-01 to FF-08", "C01 to C06", "E01 to E05", "I01 to I07", "A01 to A07", "B01 to B10",
           "TP-Link switching", "Dell Proxmox bridge attachment", "physical HP OPNsense routed filtering",
           "Windows same-zone rules", "APP1 host firewall", "Tailscale grants and device authorization", "Apache roles"),
    "F3": ("findings and hypotheses", "evidence for a verified cause", "timeout or missing log alone leaves the cause unresolved",
           "stage A–L approval before changes", "authorized change reference", "before and after evidence",
           "rollback, side effects and residual risk", "original failure and evidence", "retest date and operator",
           "new evidence ID", "actual outcome", "second observation", "both results in Office 03 Test Cases",
           "APP1 restore stays BLOCKED", "encrypted external storage and unlock/recovery",
           "exact isolated WIN1-to-restored-APP1 path through physical HP", "disconnect, reconnect and rollback"),
    "I3": ("original and retest IDs", "Office 03 Evidence Index", "source and observer UTC", "private custody",
           "sanitized reference, reviewer and redaction", "synthetic lab data", "raw records and secrets private",
           "OPEN for a new issue", "IN PROGRESS during investigation or pending retest", "BLOCKED for a dependency",
           "RESOLVED after verification", "test verdicts in Test Cases", "owner decision in Owner Acceptance",
           "Lesson learned", "verified reason if known", "what to repeat or change", "how to verify the improvement",
           "remaining limits"),
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
# OVERALL rows use the current plan in plain text. These children expose every check.
SUBCHECKS = {
    "FWT-01": (
        ("Verify ownership, recorded versions and compatibility of the prepared Dell, physical HP, TP-Link TL-SG108E and GL.iNet Beryl AX.", "Prepared equipment matches the approved inventory and supported versions.", "01 / Hardware & Readiness"),
        ("Inventory existing data and services, review backups and verify protection of the original Windows disk.", "No unapproved change to original data or services.", "01 / Hardware & Readiness"),
        ("Check both consoles, saved settings, recovery steps and exact approvals before destructive work.", "Record readiness, console recovery and the scope and date of each approval before dependent work.", "01 / Hardware & Readiness"),
        ("Trace cables, switch separation, Dell bridge/NIC membership and the physical HP path. Review alternate adapters, Wi-Fi, VPNs and sharing.", "No unapproved protected path or integration.", "01 / Network Zones"),
        ("Inspect IPv4/IPv6 routes and forwarding, protected aliases, automatic routes, router advertisements and DHCPv6.", "No unapproved protected path or integration.", "01 / Network Zones"),
        ("Inspect trust, synchronization, credentials and data boundaries.", "No home/production trust, sync, credential or data reuse.", "01 / Hardware & Readiness"),
        ("Keep Beryl AX upstream disconnected until the owner approves independent isolation, scoped egress and rollback. Inspect the approved state.", "Only approved egress is available. Home and production remain outside the path.", "01 / Allowed Network Flows / FF-07"),
        ("Verify a working allowed control. Check the approved known-listening lab-owned mock and match the denial to the effective physical HP rule, log or counter and state.", "Physical HP denies the approved mock request. All traffic stays on lab-owned targets.", "01 / Allowed Network Flows / FF-08"),
        ("Compare the private inventory to physical and firmware views. On unexpected connectivity, stop and verify console isolation and approved rollback.", "Observed hardware agrees with the private inventory.", "01 / Hardware & Readiness"),
    ),
    "FWT-02": (
        ("Verify one Dell Precision 5820 Proxmox VE host and a separate physical HP OPNsense firewall. Match Management, Corporate (DC1 and WIN1) and Restricted (APP1) to the private switch/bridge map.", "Exactly three workload VMs: DC1, WIN1 and APP1. Only the approved administrators reach Management.", "01 / Virtual Machines and Network Zones"),
        ("Compare planned allocations with observed Dell capacity. DC1 and WIN1 each use 2 vCPU / 6 GiB / 64 GiB. APP1 uses 2 vCPU / 4 GiB / 32 GiB. Measure HP capacity separately.", "Planned guest total: 6 vCPU / 16 GiB RAM / 160 GiB disk. Measured Dell capacity covers guests, host/storage reserves and temporary restore space.", "01 / Resource Allocation"),
        ("Check FF-01 through FF-08 against Office 01 and the Architecture. Review effective ingress, automatic rules, listeners, NAT and states, including FF-04 scoped APP1-to-DC1 DNS (TCP/UDP 53) and selected lab time only.", "Only approved source/service paths work. HP alone routes with default deny. Workload bridges have no host address or routing role.", "01 / Allowed Network Flows"),
        ("Demonstrate named administrator access on the approved path and supported MFA. Record the effective management rule and MFA limits.", "Only approved source/service paths work; record MFA limits.", "01 / Allowed Network Flows / FF-01"),
        ("Verify Dell and physical HP console recovery and the approved rollback separately.", "Both consoles remain available and recovery is verified.", "01 / Hardware & Readiness"),
        ("Demonstrate WIN1-to-APP1 HTTPS in an approved context. Match TCP 443 to effective HP and APP1 rules and Apache authorization.", "WIN1 to APP1 TCP 443 is permitted.", "01 / Allowed Network Flows / FF-03"),
        ("Use a working allowed control at an approved known-listening lab service. Match unlisted inter-zone denial to effective HP rule, log or counter and state.", "Default deny prevents extra access.", "01 / Allowed Network Flows / FF-08"),
        ("Compare named admin access with ordinary-user management denial before login. Match the denial to effective device or routed policy and evidence.", "Ordinary-user management access is denied; missing credentials alone is insufficient.", "01 / Allowed Network Flows / FF-08"),
        ("Inspect Windows host policy for same-zone FF-02 and independent APP1 host policy for local and overlay access. Cross-check FWT-04.03.", "Effective Windows rules constrain same-zone traffic. APP1 independently enforces its host policy.", "01 / Allowed Network Flows / FF-02"),
    ),
    "FWT-03": (
        ("Inspect ad.lab.test, DNS and Group Policy.", "Separate lab directory, lab DNS and effective policy.", "02 / Active Directory and User Roles"),
        ("Inspect ava/eli/uma, LabReaders/LabMaintainers/LabAdmins and separate privileged administrator.", "LabReaders contains ava and eli, LabMaintainers contains eli, and LabAdmins contains the separate privileged administrator only. uma is outside both application roles.", "02 / Active Directory and User Roles"),
        ("Verify standard WIN1 logon/name resolution and unintended privilege absence.", "Standard logon/DNS work; no unintended privileged membership.", "02 / Active Directory and User Roles"),
        ("C01: ava / LabReaders requests /reports/ with valid app credentials.", "Allow", "02 / Six Application Access Tests / C01"),
        ("C02: ava / no maintenance role requests /maintenance/ with valid app credentials.", "Deny", "02 / Six Application Access Tests / C02"),
        ("C03: eli / LabReaders requests /reports/ with valid app credentials.", "Allow", "02 / Six Application Access Tests / C03"),
        ("C04: eli / LabMaintainers requests /maintenance/ with valid app credentials.", "Allow", "02 / Six Application Access Tests / C04"),
        ("C05: uma / no reader role requests /reports/ with valid app credentials.", "Deny", "02 / Six Application Access Tests / C05"),
        ("C06: uma / no maintenance role requests /maintenance/ with valid app credentials.", "Deny", "02 / Six Application Access Tests / C06"),
        ("Compare manually mapped Apache groups to approved AD roles and verify separate application passwords and matching Apache authorization logs.", "Manual role mapping matches approved membership. AD single sign-on and automatic role synchronization are excluded.", "02 / Application Accounts and Permissions"),
        ("Remove eli from Apache and AD LabMaintainers under approval. Record both change times and cache treatment.", "Record exact changes and cache treatment; AD changes alone do not revoke app permission.", "02 / Access Revocation"),
        ("Force an actual maintenance request from the existing authenticated browser and match the result to Apache roles and logs.", "Revoked maintenance permission denies the existing context.", "02 / Access Revocation"),
        ("Force a fresh authenticated maintenance request. Confirm eli retains report access and compare the change and denial times with a separate clock.", "Revoked maintenance permission denies the fresh request. Report access remains allowed. Record actual elapsed time.", "02 / Access Revocation"),
    ),
    "FWT-04": (
        ("Inspect supported Windows/Linux OS builds and recorded updates.", "Supported builds and recorded update status are in place.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect Microsoft Defender, effective Group Policy and auditing on DC1 and WIN1.", "Defender, effective policy and required auditing are in place.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect Windows firewall profiles and same-zone rules. On APP1, pair approved HTTPS with a known-listening denial and match both to the effective APP1 host rule and log or counter.", "Windows host policy limits same-zone traffic. APP1 independently restricts local and overlay access. Missing listener, path or host evidence leaves this check NOT TESTED.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect standard/admin groups, single zone NIC and APP1 overlay exception.", "Separate privileges; no home/corporate profiles or bypass adapters.", "02 / Windows and Linux Endpoint Controls"),
        ("Use one approved harmless administrator-only action as a standard user. Match the denial to effective rights and policy.", "Standard users cannot administer hosts.", "02 / Windows and Linux Endpoint Controls"),
        ("Perform the same approved action as the authorized administrator and record the separate control.", "Authorized admin works.", "02 / Windows and Linux Endpoint Controls"),
        ("Inspect listeners and disabled IPv4 and IPv6 forwarding. Compare APP1 rules after the approved reboot and verify console rollback.", "No unapproved listener or forwarding path. APP1 rules persist and console recovery is verified.", "02 / Windows and Linux Endpoint Controls"),
    ),
    "FWT-05": (
        ("Inspect one encrypted offline lab CA key/public root and one APP1 leaf and restricted server key.", "One lab-only CA and one APP1 leaf. Protect both private keys and keep them out of evidence.", "02 / HTTPS Certificate Configuration"),
        ("Verify the chain, CA constraints, serverAuth purpose and SAN app.ad.lab.test.", "Correct constraints and app.ad.lab.test hostname.", "02 / HTTPS Certificate Configuration"),
        ("Inspect current dates and remaining validity explicitly.", "Certificate dates are valid; record remaining validity without changing domain time.", "02 / HTTPS Certificate Configuration"),
        ("Inspect approved-client root trust and scope.", "No lab trust outside approved clients.", "02 / HTTPS Certificate Configuration"),
        ("After importing the verified public root into an approved lab store, open the exact HTTPS name and record the trusted handshake.", "Correct chain/name/dates produce a normal HTTPS session.", "02 / HTTPS Certificate Configuration"),
        ("Before importing the verified root, use a functional untrusted lab client and record the rejected handshake.", "Untrusted client rejects the chain; no warning bypass.", "02 / HTTPS Certificate Configuration"),
        ("Record the certificate-revocation-service exclusion.", "Certificate revocation services are excluded; report that limit.", "02 / Implementation Results and Limitations"),
    ),
    "FWT-06": (
        ("Inspect the separate lab-only Tailscale tailnet and identities, supported MFA/recovery and independent isolated-egress approval.", "No production tailnet, routes, identities or credentials.", "02 / Tailscale Remote Access"),
        ("Inspect APP1 and one approved existing remote client's enrollment. Check private overlay name mapping and absence of a direct client route.", "Only APP1 and the approved existing client are enrolled for this access.", "02 / Tailscale Remote Access"),
        ("Inspect the exact APP1 TCP 443 grant, all additive rules and tag owners.", "The approved client reaches only app.ad.lab.test HTTPS. DC1, WIN1, HP and Proxmox are excluded.", "02 / Tailscale Remote Access"),
        ("Inspect routes, exit node, public share, SSH, Funnel and Serve.", "No routes/exit node/public share/SSH/Funnel/Serve.", "02 / Tailscale Remote Access"),
        ("Inspect independent APP1 overlay input/forwarding, rule precedence and Apache roles. Use HP policy/log evidence for underlay transport.", "Effective host/overlay policy restricts the single resource. Attribute each denial to the actual grant, device, host or application control.", "02 / Tailscale Remote Access"),
        ("Demonstrate the approved existing client's working HTTPS control with Apache roles and match the request to effective policy and logs.", "Approved remote HTTPS works with app roles.", "02 / Tailscale Remote Access"),
        ("Demonstrate unauthorized remote identity denial with a working HTTPS control and matching effective grant/device or host evidence.", "Wrong identity cannot access the resource.", "02 / Tailscale Remote Access"),
        ("Use a working control on a known-listening wrong port. Use an approved lab-owned mock for any required wrong-resource check. Match each denial to the effective control and device, host or log evidence.", "Wrong port/resource cannot be reached.", "02 / Tailscale Remote Access"),
        ("Reconfirm working approved HTTPS, then remove the exact client's grant and device authorization. Record both change times and cache/connection-state handling.", "Authorization is revoked; record exact change/cache/state treatment.", "02 / Access Revocation"),
        ("Force an actual network request from the existing authenticated remote session. Record denial time and matching grant, device or host evidence.", "Revoked client cannot access it through existing requests.", "02 / Access Revocation"),
        ("Force a fresh remote request and record denial with effective control evidence. Compare both denial times with the changes using a separate clock.", "Revoked access is denied in the fresh session. Record elapsed time for both sessions. Missing approved egress or denial evidence leaves the check NOT TESTED.", "02 / Access Revocation"),
    ),
    "FWT-07": (
        ("Review approved sources, access and rotation. Compare actual DC1 Security, APP1 Apache and physical HP OPNsense source and observer times in UTC.", "Restricted logs/rotation; source/observer UTC/time differences recorded.", "03 / Security Events"),
        ("Verify DC1 account-logon auditing and relevant Kerberos records.", "Do not assume a WIN1 interactive event is recorded on DC1.", "03 / Security Events / E01-E02"),
        ("Record directory logon success.", "Attributable/searchable source record for directory success.", "03 / Security Events / E01"),
        ("Check lockout margin. Record one safe wrong-password attempt and match the actual DC1 Kerberos event.", "Attributable/searchable source record for one failure.", "03 / Security Events / E02"),
        ("Record application allow.", "Attributable/searchable source record for app allow.", "03 / Security Events / E03"),
        ("Record authenticated application denial.", "Attributable/searchable source record for authenticated app denial.", "03 / Security Events / E04"),
        ("Record E05 from physical HP OPNsense. Match the lab-owned denied request and timestamp to the effective HP rule and source log or counter.", "Attributable/searchable source record for firewall denial.", "03 / Security Events / E05"),
        ("Investigate one approved lab-owned denial with a known working allowed control. Match the source, destination, service and time to effective rule/role and log, state or counter evidence.", "Explain who requested what, why denied and supporting evidence.", "03 / Denied Access Investigation"),
        ("Compare actual action, source time and effective control as a second observation. Link evidence and keep raw originals in private custody.", "Five distinct event categories; no duplicate-request substitution.", "03 / Evidence Index"),
    ),
    "FWT-08": (
        ("Review approval and version for one manual WIN1 disk-capacity summary run locally as a standard user.", "One approved local read-only capacity query and protected private output. No unapproved elevation or writes.", "03 / Automation Verification / A01-A02"),
        ("Verify WIN1/ad.lab.test target guards, output-path guards and private output permissions.", "WIN1/ad.lab.test target and reviewed private path only.", "03 / Automation Verification / A02"),
        ("Execute once and compare to the OS storage view.", "Intended summary is correct.", "03 / Automation Verification / A03"),
        ("Repeat the same approved standard-user run locally and compare actual output and side effects.", "Both runs report accurate capacity. Only the intended private summary changes.", "03 / Automation Verification / A04"),
        ("Safely check invalid target rejection.", "Invalid target is rejected without a write.", "03 / Automation Verification / A05"),
        ("Safely check invalid path rejection.", "Invalid path is rejected without a write.", "03 / Automation Verification / A06"),
        ("Compare before/after files, accounts, network and system settings for both runs and both rejections. Review public contents.", "No unintended changes; no credential/private inventory published; time/free-space may vary.", "03 / Automation Verification / A07"),
    ),
    "FWT-09": (
        ("Verify exact APP1 scope and both recovery approvals in Reference 07 before the drill. Keep unperformed checks NOT TESTED.", "Pages/config/hashed app accounts/roles/server key/leaf/public root are covered.", "03 / Backup & Restore / B01"),
        ("Verify the approved encrypted external backend, unlock/recovery procedure, off-compute archive and separate recovery-key access.", "One encrypted off-compute backup; same-disk snapshots do not qualify.", "03 / Backup & Restore / B02"),
        ("Record actual backup time/age, archive coverage and the independently retained original manifest reference.", "Actual backup age/time and scope recorded.", "03 / Backup & Restore / B03"),
        ("Verify original APP1 stopped before backup and throughout the drill. Preserve the sole archive. Use the approved unused temporary ID with all restored NICs disconnected and autostart off.", "No overwrite of original/sole backup or duplicate live identities.", "03 / Backup & Restore / B04"),
        ("Verify copied Tailscale is stopped and disabled before any approved client attachment.", "No connected duplicate overlay identity.", "03 / Backup & Restore / B05"),
        ("Measure from restore confirmation until verified manifest integrity and usable HTTPS. Compare with a separate clock.", "Actual scoped restore succeeds; no enterprise RPO/RTO threshold.", "03 / Backup & Restore / B06"),
        ("Compare restored hashes and declared content to the independently retained original manifest before attachment. Verify the Reference 07 command in the approved execution-stage shell.", "Restored data matches the declared manifest/content.", "03 / Backup & Restore / B07"),
        ("Use only the owner-approved isolated WIN1-to-copy path through physical HP OPNsense and the approved narrow temporary settings. Verify the disconnect, reconnect and rollback checklist. Keep upstream and nonparticipants disconnected.", "Trusted restored HTTPS works on the exact approved physical path. Record matching HP and APP1 evidence. The drill is BLOCKED until both Reference 07 prerequisites are approved.", "03 / Backup & Restore / B08"),
        ("With valid ava credentials over trusted HTTPS, verify reports allowed and maintenance denied. Match roles and requests to Apache logs.", "Restored authorization allows/denies the approved roles.", "03 / Backup & Restore / B09"),
        ("Disconnect and stop the copy before rolling back temporary settings. Verify original APP1 final state and encrypted off-compute custody. Record AD, CA, Dell host and physical HP recovery exclusions.", "Recovery claims stay within APP1 scope; original and backup preserved.", "03 / Backup & Restore / B10"),
    ),
    "FWT-10": (
        ("Review all 91 mandatory subchecks, mapped controls, actual evidence, second observations and defects.", "Every mandatory check has traceable evidence. Critical and high safety issues are resolved.", "03 / Requirements Coverage and Evidence Index"),
        ("Complete the five released submission files named above. Apply the Assignment's 100-point rubric to verified evidence.", "Five final files present; claims supported; rubric totals 100.", "05 / Final Evaluation and Supporting Deliverables and Evidence"),
        ("Scan/review proposed public contents, metadata, staged diff and new history.", "Only reviewed sanitized artifacts/history are published.", "03 / Evidence Index"),
        ("Run finalized-report, links and Office validation.", "Required documentation/report checks pass.", "03 / Evidence Index"),
        ("Run PDF/rebuild, focused regression and whitespace checks.", "Required document checks pass; no Office/report PDFs generated.", "03 / Evidence Index"),
        ("Verify actual PR and exact final-head CI.", "Intentional publication is verified at the exact head.", "03 / Evidence Index"),
        ("Verify the observed merge and matching local, tracking and live main IDs.", "Observed merge and live synchronization recorded.", "03 / Evidence Index"),
        ("Record the engineering verifier and evidence cutoff. Compare actual lab claims with Evidence Index and private originals.", "Engineering results reflect actual lab evidence. GitHub CI records documentation validation.", "05 / Final Evaluation"),
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


def office03_test_rows(plan: str) -> list[list[str]]:
    """Return the ordered summary and mandatory child rows in worksheet text."""
    rows = []
    for definition in approved_tests(plan):
        tid, rid = definition["id"], definition["requirement"]
        method = "\n".join(definition[key] for key in ("title", "scope", "method"))
        text = [
            re.sub(r"\[([^\]\n]+)\]\([^)\n]+\)", r"\1", value).replace("**", "").replace("`", "")
            for value in (method, definition["expected"], definition["second"])
        ]
        rows.append([tid, rid, "OVERALL", *text])
        rows.extend(
            [tid, rid, f"{tid}.{i:02}", action, expected, detail]
            for i, (action, expected, detail) in enumerate(SUBCHECKS[tid], 1)
        )
    return rows
