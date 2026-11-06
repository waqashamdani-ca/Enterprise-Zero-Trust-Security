# T6B - Lab Implementation Guide usability, language and layout refinement

Report state: DRAFT

## A. Task Information

| Field | Record |
| --- | --- |
| Task ID | T6B |
| Execution date | 2026-11-06, America/Toronto |
| Authority | Owner's T6B Lab Implementation Guide Usability, Language and Layout Refinement request, 2026-11-06; private original retained by owner |
| Authorized scope | Guide Markdown/PDF; guide-specific rendering; focused validation/tests; generated manifest; necessary build/navigation references; Markdown-only report; reviewed GitHub branch/PR/CI/merge/synchronization |
| Dependency | T6A FINALIZED; PR 8 merged; main workflow 42275431573 SUCCESS; local main, origin/main and live main a3d7b1c6effde3bd5b18ab1a4b529c07a7cc7c61 before work |
| Branch / preservation | codex/006b-guide-usability in a clean isolated worktree pulled from main with --ff-only; original checkout retains its same five owner archive-PDF deletions |
| Reporting exception | Owner expressly requested T6B-Report.md as a T6 companion, after completed T6A publication; no T7 allocation or implicit authorization of other lettered tasks |
| Dependencies | Existing bundled Python 3.12.14, pinned documentation packages and Poppler; no lab software/font installation, Office edit or lab operation |

The owner needs instructions that identify the action, target, tool, setting, expected result, verification and recovery. Targets were intact exact filenames, no internal task jargon, five consistent A-H phases, explicit command context, accurate version-dependent navigation, unchanged scope/commands/mappings, searchable linked PDFs and every-page visual review.

Risks reviewed were scope/semantic drift, misleading readiness or identity claims, incorrect menus or command context, broken navigation, clipping and public disclosure. No architectural decision, requirement, test expectation or risk acceptance changed. Existing risk/decision registers remain authoritative. Rollback is a normal reviewed revert of editable documentation/code/generated artifacts, preserving finalized reports, evidence and owner work.

## B. Implementation Summary

| Changed file | Result |
| --- | --- |
| [LAB-IMPLEMENTATION-GUIDE.md](../lab-guides/LAB-IMPLEMENTATION-GUIDE.md) and adjacent PDF | Practical numbered procedures, consistent eight-part phases, essential navigation and accurate expected/verification/recovery instructions |
| [build_docs.py](../../scripts/build_docs.py) | Exact-guide-path typography/header/compact contents, readable code, intact filename column, clean tables, complete numbered steps and phase spacing |
| [validate_docs.py](../../scripts/validate_docs.py) | New guide headings/availability/jargon/context and existing phase-test/safety contracts; explicit protected T6B companion exception |
| [test_build_docs.py](../../tests/test_build_docs.py), [test_validate_docs.py](../../tests/test_validate_docs.py) | Real-PDF whole filenames/steps/navigation, unchanged command blocks and unrelated assets; negative guide/governance cases for both authorized companions |
| Generated manifest | Builder-produced current source/PDF/renderer hashes and navigation data; no manual hash suppression |
| [DOCUMENTATION-BUILD.md](../governance/DOCUMENTATION-BUILD.md) and PDF | One necessary paragraph describes guide-specific layout; all other source content unchanged |
| [Report index](INDEX.md), this report | Companion navigation and explicit owner-authorized naming; Markdown only |

Eleven scoped paths, ten changed existing files and this new report. Seventy-one of the 81 baseline tracked files remain byte-identical, including the assignment source/PDF, architecture, security/test/acceptance specifications, rubric, decisions/risks, AGENTS.md, historical evidence/reports and all eight legacy Office templates. Exactly two PDFs change; 22 unrelated/archived PDFs retain their bytes.

| Measure | Before | After |
| --- | --- | --- |
| Guide PDF pages | 15 | 18 |
| Guide source words | 3,565 | 6,500 |
| Phase organization | Seven uneven fields per phase | Eight A-H fields: objective, prerequisites, tools, steps, expected results, verification, troubleshooting, recovery |
| Filename table | Several names split on page 14 | All five exact filenames intact on single lines together on page 17 |
| Front matter | Separate cover/contents, repeated internal status language | Compact title/linked contents and natural preparation instructions |
| Reference command/configuration blocks | Eleven | Same eleven, identical language/content/order |

Word count is len(source.split()) on UTF-8 Markdown including tables/links/code; the same method is used before/after. Added words supply missing navigation, command context and recovery detail. Three added pages preserve practical instruction completeness; the implementation target stays four weeks. No readability score or measured owner usability is claimed.

Every phase now uses A-H consistently. Numbered actions separate preparation from changes and identify where/how to act. Internal T6/T7/Codex wording was removed from the guide; PLANNED, NOT TESTED and PENDING remain explicit. Historical requirement/test transition tables and their incoming links remain intact. Templates remain planned/unavailable; no submission filename or definition changed.

| Area | Practical navigation / context added |
| --- | --- |
| Proxmox | Host/Disks/storage inspection, System > Network bridges, Create VM, Hardware network assignment, Console, Backup/Restore and disconnected-copy safeguards |
| OPNsense | Interfaces > Assignments with MAC mapping; Firewall > Rules fields/order; Live View filtering; password-protected configuration backup |
| Windows | Server Manager role/promotion, users/groups, DNS record, domain join, Group Policy/firewall, endpoint privilege view and certificate import |
| Linux / Apache | Console network/resolver/firewall fields; selected-backend/version gate; conditional Ubuntu file locations; site/modules/log paths, syntax check and recorded service activation/status |
| Tailscale | Separate lab identity/MFA, explicit deny-all before enrollment, exact observed APP1 identity before its narrow grant, Machines inspection/removal and existing/fresh denial |
| Monitoring / recovery | Event Viewer source/filter context, five event categories, private capacity-summary invocation/comparison, exact backup/restore target and isolated validation |

Important commands/configuration identify OS/target, shell/editor, elevation, purpose, private replacements, expected output and a confirming observation. READ-ONLY, CONFIGURATION CHANGE and DESTRUCTIVE / HIGH-RISK labels distinguish effects. Secure prompts and overwrite cautions remain. The capacity script is still reference text, not a created executable or executed lab operation. Markdown remains the command source; PDF wrapping is identified as visual.

Technical review used primary vendor guidance: [Proxmox GUI](https://github.com/proxmox/pve-docs/blob/master/pve-gui.adoc), [network](https://github.com/proxmox/pve-docs/blob/master/pve-network.adoc) and [backup](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc); [OPNsense interfaces](https://docs.opnsense.org/manual/interfaces.html), [rules](https://docs.opnsense.org/manual/firewall.html), [logs](https://docs.opnsense.org/manual/logging_firewall.html) and [backup](https://docs.opnsense.org/manual/backups.html); Microsoft and Apache/OpenSSL links beside the relevant procedures; [Tailscale grants](https://tailscale.com/docs/reference/syntax/grants), [deny-all example](https://tailscale.com/docs/reference/examples/acls#deny-all) and [device removal](https://tailscale.com/docs/features/access-control/device-management/how-to/remove).

Two details were clarified without changing requirements or existing commands: domain-account password policy uses a domain-root GPO rather than an OU-only link ([Microsoft](https://learn.microsoft.com/windows/security/threat-protection/security-policy-settings/password-policy)); enrollment starts with explicit empty ACLs/no additive allows, then exact APP1 is identified before adding TCP 443 access. The actual tailnet/OS/backend remains unselected/unvalidated. Current OPNsense guidance distinguishes modern and legacy screens; the guide requires installed-version label checks.

Direct Proxmox admin HTML returned 403 and systemd HTML timed out; official Proxmox source and [systemd journalctl source](https://github.com/systemd/systemd/blob/main/man/journalctl.xml) supplied the documented fallback. Vendor syntax/navigation research establishes no installed-version compatibility or runtime success. The [reference catalog](../governance/REFERENCES.md) remains unchanged.

Scope preserved: one Proxmox host/four VMs/three zones; three standard users/role groups and one separate privileged administrator; separate AD Windows and manual app identities; one CA/HTTPS leaf; Tailscale-only one-resource access; two or three log sources/five events/one denial investigation; one automation; one encrypted backup/isolated restore; six app cases; ten FWR/FWT mappings and the existing 25/25/20/20/10 rubric. No extra permanent VM, lab tool requirement, operational test or deliverable was added. All A-L approvals, original-disk/data/service preservation, verified recovery, independently isolated egress, lab-only targets and separate UAT remain.

## C. Testing and Validation

Engineering verifier: Codex. Rendered/source/Git observations below are separate methods by the same verifier, not independent human approval. Raw previews/logs and baseline records stay in ignored private work locations.

| Executed command/check / expected outcome | Actual observation | Verdict |
| --- | --- | --- |
| T6A/GitHub/preflight | Finalized report hash, merged PR 8, successful main CI, exact local/live main baseline, authenticated owner push/admin permissions and original changes verified | PASS |
| Existing source/PDF review | 15-page baseline; page 14 shows wrapped filenames; source/context specifications reviewed | PASS |
| Vendor/semantic/manual review | Required counts, roles, approvals, test expectations and command behavior retained; release-specific backend/labels explicitly gated | PASS for documentation; runtime NOT TESTED |
| python scripts/build_docs.py | 19 maintained pairs/81 pages; guide 18 pages, build guide 3; only those two PDF bytes changed | PASS |
| python scripts/build_docs.py --check --rebuild-check | Fresh in-memory bytes, source/hash/text/navigation/metadata match; guide text-token coverage 1.0 | PASS |
| No-change build plus independent SHA-256/mtime snapshot | All 24 maintained/archive PDF hashes and modification times unchanged | PASS |
| python scripts/validate_docs.py | 82 candidates/38 Markdown files; links, mappings, phase fields, workflow/publication and report/history/migration checks pass | PASS |
| python scripts/validate_office_templates.py | Eight old packages/30 worksheets and pinned blank-shell definitions preserved | PASS |
| python -m unittest discover -s tests -v | 69 tests PASS; real PDF keeps every numbered step on a page and all filenames whole; unchanged reference blocks/other assets; companion modification/deletion and invalid-name/parent/state negatives | PASS |
| Independent baseline hashes and committed-byte comparison | 71 baseline files unchanged; assignment, core specifications, Office files and frozen reports/evidence intact; 22 other PDFs unchanged | PASS |
| Every-page Poppler visual review | All 18 guide pages and all 3 supporting build-guide pages reviewed; no clipped code, overlap, broken rows, split filenames, orphan headings or unnecessary empty page observed | PASS |
| Final minor clarification/whitespace rebuild comparison | Only guide page bodies 6 and 10 changed and were reinspected; all other already-reviewed page bodies match pixel-for-pixel excluding source-version footer; final whitespace-only rebuild preserves all 18 already-reviewed page bodies | PASS |
| git diff --check and manual full proposed content/code/PDF/history review | Corrected trailing empty line; scoped source/code/metadata/public-safe content reviewed | PASS |
| Finalized-report completion gate | To run after finalization and before merge; not yet run for a finalized T6B state at this draft observation | NOT TESTED |
| Lab implementation/security tests, installed-version GUI/commands, readiness and owner UAT | No lab operation; no actual implementation/acceptance evidence | NOT TESTED / PENDING |

One initial negative fixture failed because availability wording was duplicated; the prerequisite now points to the authoritative deliverable status, and all 69 tests pass. Visual iterations reduced the first 20-page build to 18 with compact contents/phase flow and kept numbered steps intact. A trailing empty line was removed. These corrected development findings are not passing operational tests.

Poppler emitted Symbol/ArialUnicode display-font warnings; reviewed text/glyphs remained legible with the embedded document fonts. Extraction checked searchable content/links, while rendered pages checked layout. Final output inspection does not establish owner acceptance.

## D. Security and Quality Review

No lab hardware/software installation, disk selection, VM creation, network/firewall change, directory deployment, Tailscale enrollment or lab test was performed. The four-week baseline remains planned. Documentation validation reaches no lab target and executes no guide example. No Office file was edited/regenerated, and no historical report/PDF was regenerated or rewritten.

The proposed public set includes reviewed sources, the two generated PDFs, manifest, focused code/tests and reporting navigation only. New text uses reserved lab names/symbolic private values, not actual addresses, credentials, inventory serials, procurement IDs or raw evidence. Manual review supplements bounded scanners. No license, account privacy, workflow privilege, ruleset or reviewer setting changed; no scanner/protection bypass is permitted.

## E. GitHub Operations

Authorized existing repository is public, default main. Authenticated owner waqashamdani-ca has push/admin permissions. Original lowercase origin redirects to the same verified case-renamed repository and is preserved. Global Git identity/account settings remain unchanged; new author and committer must use the verified owner noreply identity.

Branch codex/006b-guide-usability began from clean isolated main at a3d7b1c6effde3bd5b18ab1a4b529c07a7cc7c61. At this draft observation no T6B commit/PR/CI/merge/synchronization is claimed. Finalization will record observed initial publication evidence; its own later publication/CI/merge/main results belong in the final chat response without editing the finalized record.

## F. Outstanding Issues

No known unresolved documentation/design/test failure. Installed versions/backends and exact Linux activation paths require stage-entry verification. Delivery, compatibility, original data/service readiness, encrypted recovery media, independent egress and individual A-L approvals remain future dependencies. No operational result or risk acceptance is inferred.

Owner UAT PENDING; independent human review NOT TESTED. The original checkout is not clean: its five pre-existing owner archive-PDF deletions remain untouched. Finalized-report gate and final publication/CI/merge/synchronization remain pending at this draft observation. Five new templates remain unavailable until separately authorized migration.

## G. Completion Status

| Area | State |
| --- | --- |
| Guide editorial/usability/layout work | IMPLEMENTED / locally VALIDATED by the checks above |
| Second observations | PASS through source/PDF/render, independent baseline hashes and GitHub preflight; same engineering verifier |
| Independent human review | NOT TESTED |
| Report / publication | DRAFT / pending |
| Operational lab implementation | PLANNED / NOT TESTED; no action performed |
| Owner UAT / acceptance | PENDING |

## H. Next Task

Recommend **T7 only**: migrate the eight legacy Office shells to the five approved templates after explicit owner approval of scope, exact filenames, preservation/replacement rules, requirement/test/rubric mappings, native/visual/formula validation and rollback. Do not begin T7 or a lab implementation stage during this task. Stop after T6B publication/synchronization and await owner review.
