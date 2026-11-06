# Evidence handling

This public folder accepts only individually reviewed, sanitized evidence. Raw captures, logs, backups, screenshots, and exports stay in private owner-controlled storage outside the repository. Task 001 does not create implementation evidence.

For each future record, include an evidence ID (`EV-<test>-<date>-<sequence>`), requirement and test IDs, stage, UTC timestamp, tool/version, scoped synthetic source/target roles, expected and observed outcome, verdict, operator, independent verification method, and sanitization review. Record engineering verification and owner UAT in separate fields. Mark missing evidence **NOT RUN**, not passing.

Suggested public filename: `EV-T06-YYYYMMDD-01.md`. Preserve original evidence privately with a SHA-256 digest and a private custody record. Hash the sanitized artifact separately; do not imply that it is byte-identical to the original. Publish only necessary synthetic excerpts, redact addresses and identifiers, and inspect the rendered image/text and metadata. Keep private record locations out of public reports.

The [test plan](../docs/TEST-PLAN.md) defines the future evidence required for each outcome. Documentation check results support repository quality only and cannot demonstrate operational security.
