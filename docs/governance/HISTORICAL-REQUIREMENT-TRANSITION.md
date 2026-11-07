# Historical requirement and test transition

This navigation appendix preserves the earlier requirement/test mappings. It is historical reference, not an implementation procedure or an expansion of the four-week assignment. Current requirements, test methods and evidence remain in the [assignment](../assignments/PROJECT-ASSIGNMENT.md) and [Test Plan](../testing/TEST-PLAN.md). No historical result transfers to a current operational test.


FWR/FWT identify the current four-week requirements/tests. Earlier R01-R16/T00-T20 retain their meanings in frozen reports/history and legacy templates; no historical PASS transfers to a new operational test. Old quantities below are historical, not current work.

| Earlier requirement | New requirement | Consolidation or retirement |
| --- | --- | --- |
| R01 | FWR-01 | Isolation retained |
| R02, R03, R04 | FWR-02 | Capacity/admin; six zones become three |
| R05, R08 | FWR-03 | Six standard/two privileged users become three/one; twelve cases become six plus revocation |
| R06 | FWR-04 | Windows endpoint/Linux app, no extra endpoint |
| R07 | FWR-05 | Two-tier/revocation service becomes one CA/leaf, trust/expiry |
| R09 | FWR-06 | Dual pilots become one-resource Tailscale |
| R10 | FWR-07 | Six sources/twenty-event latency/retention targets become two or three sources/five events/investigation |
| R12 | FWR-08 | Two operations become one |
| R13 | FWR-09 | Enterprise objectives become measured APP1 restore |
| R11, R14, R15, R16 | FWR-10 | Hygiene, focused evidence, governance/submission/UAT retained |

| Earlier tests | New test | Treatment |
| --- | --- | --- |
| T01, T02, T03 | FWT-01; capacity also FWT-02 | Isolation/readiness/conditional egress using mocks |
| T04, T05, T06 | FWT-02 | Management/permits/default deny/same-zone host controls |
| T07, T08, T12 | FWT-03 | AD, six app cases and app revocation |
| T09 | FWT-04 | Endpoint baseline |
| T10, T11 | FWT-05 | Trust/name/expiry; certificate-revocation test retired |
| T13, T14 | FWT-06 | Tailscale only; Twingate retired |
| T15, T16 | FWT-07 | Time notes/five events/investigation |
| T18 | FWT-08 | One operation plus repeat/rejection |
| T19 | FWT-09 | APP1 restore, actual time/limits |
| T00, T17, T20 | FWT-10 | Publication/traceability/separate UAT |

See [decisions](../governance/DECISIONS.md), [risks](../governance/RISKS.md) and [end-to-end coverage](../testing/TEST-PLAN.md#coverage-index). High availability/clustering remain excluded.
