# Acceptance scenarios

Use a separate clearly labeled test course/rows; never impersonate a real university requirement. A live smoke test was run on 2026-11-11, with data read back after writes. Test work is archived, opportunities are inactive, and the test plan is in history.

| Scenario | Verified live result |
| --- | --- |
| Ready work, postponed defense | Only opportunity date/state changed; ready status and zero remaining hours survived |
| Instructor no-show | Opportunity became “Не відбулася”; work stayed ready |
| Another group permits defense | Separate related opportunity created with its own group, source and confirmation |
| Weekly work unfinished | Earlier recommendation retained in plan body; remaining work unchanged |
| Work harder than expected | Remaining estimate updated from 4 to 9 hours and read back |
| New urgent deadline | Priority/plan fields updated; test deadline 2026-11-16 remained unchanged |
| Insufficient semester capacity | Test demand 13.25 hours vs 8 usable hours; 5.25-hour deficit recorded, selected effort stayed 8 hours |

These are integration and agent-directed smoke checks, not an independent evaluation proving future model behavior. There is no deterministic planning engine. Future runs must reason from current data and obey planning.md. Multiuser races, injected transient Notion failures and autonomous rollback have not been exercised end-to-end.

Automated helper checks: Windows-1251/CR, UTF-8, timezone, invalid HTML, changed headers, out-of-range dates, malformed row, stable source keys, header-only exports, invalid period/ID and preserving good cache after a failed parse. Live official schedule requests returned 19 group events and 2 teacher events for 2026-11-09–15. The instructor was an arbitrary official-directory test identity, not a claim about the user's instructors.

## v2 scope
The historical numeric-hour smoke cases above tested v1 storage, not a v2 duration model. v2 uses ordinal course effort and active attention budget; it must not calculate fictitious task hours or precise semester deficits from categories. Actual v2 course fields, view visibility and settings have been checked in live Notion. CSV helper now also has two checks for role-specific instructor mapping and missing HTML legends (12 automated checks total).
