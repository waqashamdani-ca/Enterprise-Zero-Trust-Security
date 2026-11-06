# Project execution and repository governance

Applies to this repository and every subdirectory. Project: **HL-CYB-001, Enterprise Zero Trust Security Architecture**.

## Authorized task and stop condition

Task 001 is limited to planning, documentation, scaffolding, focused documentation checks, safe Git initialization, and reviewed public GitHub publication/synchronization. These actions are already authorized by the owner. Complete that bounded task, then stop for owner review. Do not install software, create VMs, change networks, run security tests, or start an implementation stage during Task 001.

For future work, require **explicit owner approval before each implementation stage A–L** in the implementation guide. Approval must identify the stage, scope, assets, permitted changes, validation, and rollback. Approval of a document, a PR, or a previous stage does not authorize the next stage. Record an approval reference and date without publishing private conversations. A missing approval means dependent implementation does not proceed; read-only planning within the current authorization may continue.

## Engineering method

1. Work on one bounded task at a time. Read the assignment, architecture, requirements, applicable decisions, and current status before changing anything.
2. Inspect existing files, Git status, remotes, branches, and relevant tooling first. Preserve existing work. Identify conflicts before proposing a reconciliation; do not overwrite or delete owner content without approval.
3. Use documentation-first execution: update the proposed design, measurable outcomes, threat model, affected requirements, test plan, and rollback before implementation.
4. Verify current vendor documentation and version-specific commands. Label proposed commands and identify their target. Never execute a guide merely because it exists.
5. Make the smallest useful change. Do not introduce installation, deployment, attack simulation, remote connectivity, or production access through a validation script or workflow.
6. Use focused automated checks appropriate to the change. Independently verify outcomes through a second observation, such as a policy inspection plus a bounded positive/negative connection test. Re-running the same command is not independent verification. Do not claim independent reviewer sign-off unless someone else actually reviewed it.
7. Separate **engineering verification** from **owner user acceptance testing (UAT)**. A CI pass does not approve business behavior or stage advancement. Record each result, reviewer role, evidence, date, and unresolved issue.
8. Report proposed, implemented, verified, failed, blocked, and accepted states accurately. Attach sanitized evidence to each claimed result. Never turn a planned test into a passing result.
9. Track architectural choices and changes in [DECISIONS.md](docs/DECISIONS.md), risks in [RISKS.md](docs/RISKS.md), requirements/tests in their respective documents, and actual completion in [FINAL-REPORT.md](docs/FINAL-REPORT.md).

## Production and destructive-operation boundaries

Use synthetic business data, separate lab identities, separate remote-access environments, and isolated lab resources. No production trust, federation, identity synchronization, credential reuse, corporate Microsoft 365 connection, PE-DAP source code, customer data, corporate website access for testing, or production hosting integration is permitted.

No destructive operation, disk installation/formatting, trust creation, route publication, firewall change, exposure to the Internet, or production operation without explicit authorization covering that action. Proxmox installation must never select a disk until the owner has approved its exact identity and backup/recovery plan. If unexpected connectivity or possible production impact appears, stop the affected operation, isolate the lab using the approved recovery procedure, and report facts.

No security probes, scans, password attacks, malware, exploit execution, or attack traffic outside an explicitly approved lab scope. Home and production isolation is verified through configuration inspection, passive observation, and lab-owned mock protected targets; never actively probe real protected networks to demonstrate a deny rule.

## Public repository and secrets

Publish only reviewed public-safe artifacts. Keep tokens, passwords, private keys, lab inventories and actual addresses, corporate details, raw evidence, logs, packet captures, VM images, state files, and backups outside the public repository. `.gitignore` is not a security boundary and does not remove already tracked files. Never store authentication tokens in project files, Git URLs, command arguments, screenshots, or commit messages. Use GitHub CLI/Git Credential Manager or another supported secure credential store.

Before every publication, inspect the complete proposed tracked set, staged diff, filenames, and new history; run the validator and relevant checks. Resolve all findings and perform a manual sensitive-data review. Do not bypass scanners to publish a finding. Synthetic examples must use reserved names or symbolic address variables. If a secret is exposed, stop publication, revoke/rotate it using the owner's authorized incident process, preserve private incident evidence, and obtain approval for any history rewrite.

Never select a software license without owner approval.

## Git and GitHub conventions

- Authorized repository: [waqashamdani-ca/enterprise-zero-trust-security](https://github.com/waqashamdani-ca/enterprise-zero-trust-security), **PUBLIC**, default branch `main`.
- Verify the authenticated identity and repository permissions before writing. Use a GitHub noreply author email for public commits. Never alter global Git configuration as part of a project task.
- Check whether the remote exists before creating it. Inspect existing branches and contents, reconcile changes on a branch, and preserve history. Never force-push or overwrite existing work without explicit owner approval.
- The initial reviewed Task 001 bootstrap may initialize `main` directly in a new empty repository. Future engineering uses task branches, for example `task/002-hardware-readiness`.
- Begin from clean `main` and `git pull --ff-only origin main`. Stop on divergence; do not use an automatic merge, destructive reset, or forced update to conceal differences.
- Stage explicit public-safe paths. Make focused commits with meaningful messages, push the task branch, run applicable CI/security checks, and use a PR for review before merging into `main`.
- PRs describe the problem, resulting behavior, scope, affected requirement/test IDs, validation evidence, risks, rollback, and applicable owner approval. Stage approval and owner UAT remain distinct records.
- After merge, fast-forward local `main`. Confirm `git remote -v`, `git status`, `git branch -vv`, `git log -1`, and `git ls-remote origin`; verify the local and remote commit IDs agree.
- Synchronization is intentional Git activity. Never enable background upload or treat all local files as publishable.
- Workflows use least privilege (`contents: read` unless a reviewed task requires more), commit-pinned official actions, no persistent checkout credentials, no secrets in fork PR checks, and no lab access. Do not use `pull_request_target` to execute untrusted PR code.
- Repository rulesets, required checks, reviewer settings, and licensing require explicit owner decisions; do not silently change them.

## Completion report

State changed files, checks actually run, local/remote commit IDs, repository URL, visibility/default branch, CI result, owner UAT status, unresolved decisions/risks, and exactly one recommended next task. Stop at the authorized task boundary.
