# Notion writes and recovery

## Discovery and scope
Use the configured hub, not broad workspace redesign. Fetch database/collection schemas first and use exact field names. Read `notion://docs/notion-flavored-markdown-spec` and `notion://docs/view-dsl-spec` through Notion fetch when needed. Native page/collection mentions for internal links, date mentions for content dates. Schema permissions do not imply sharing/deletion permissions.

For imports use an explicit stable `Ключ імпорту` per source record; query existing keys before create. Similar names alone are not safe identity. Where source IDs are absent, propose matches for review. Preserve completion and real deadlines on refresh. New work defaults explicitly to `До виконання`; explicitly set whether defense is needed after reading rules (an unchecked box is not evidence).

## Publish one weekly plan
1. Locate the week by `Ключ тижня` (semester identity + ISO Monday), not title only. More than one match is a conflict to resolve, not permission to delete. New plan is `Чернетка` with an operation UUID. Re-read a timed-out create by its key/operation before retry.
2. Fetch current plan and task fields. Keep a dated, labeled snapshot of the old recommendations inside the plan's `Історія переглядів`, including old focus fields and reasons. Record a small operation journal: intended changed fields with old/new values. Do not snapshot whole private unrelated pages.
3. Mark existing plan `Потребує перегляду` while changing it; prepare new content in its draft section. For each task patch only plan relation, Monday `Тиждень фокусу`, Sunday `Кінець фокусу`, optional `План год` only for explicit time allocations, priority, next step, reasons, and operation ID. Do not patch completion, remaining hours or deadline as part of planning. Clear obsolete focus only after preserving the snapshot, and only for the previous current plan in this semester.
4. Re-read touched task fields immediately before updates. If changed from the read snapshot, recompute/merge; never blindly restore an old value. On failure stop publication, report affected IDs and mark the plan `Потребує перегляду` or keep draft. Readback after writes verifies values; retry only after reading actual state. Limit retries to two after transient errors, honoring Retry-After.
5. Verify attention budget, task references, workload uncertainty and written content. Sum time allocations only when explicitly made; do not invent required hours from effort categories. Publish `Актуальний` only after every required write succeeds. Mark an older week's plan `Історія` when its period has ended, as part of the authorized weekly rollover. Set `Кінець тижня` to Sunday. Update settings' current-plan link last. A failed last step is reported explicitly.
6. On replay, inspect journal and operation IDs. Continue incomplete steps only when preconditions still match. Do not create another plan for the same week.

## Restore
Restore recommendations from a chosen snapshot into a new revision using the same publication process. Re-evaluate against current factual task state; omit already-credited work. Never undo later human progress/deadline changes. General Notion version restore is not the default because it could revert unrelated edits.

## Honest boundaries
These steps reduce errors; they are not atomic transactions or background conflict locks. Human edits may occur between calls. Manual Notion edits do not automatically trigger replanning. Plans show last calculated time; agent checks live state before use and can mark stale plans. No external sync process is claimed.

## Verified connector details
Page replacement uses `new_str`; insertion uses `content`. Fetch returns escaped bracket characters in plain-text properties; normalize Markdown escaping of punctuation (including colons in import keys) for identity assertions, never alter the underlying user value just for that reason. Formula filters may be silently omitted by the view tool: inspect returned filters and use supported date fields instead. Use saved-view or paginated rows mode for routine reads; SQL can have plan-dependent quotas.

## Default reads on limited Notion plans
Prefer `mode: view` with a fetched default/all-work view and paginate via next_cursor. Inspect its filters first: a weekly-focus view is not the inventory. Need archived work? Read the relevant view with is_archived as supported or fetch exact IDs. rows and SQL share a plan-dependent allowance and can become unavailable. If limited, do not retry or require a paid upgrade: switch to a suitable saved view or exact page reads, disclose the limit and continue. Preserve correct scope; don't mutate view filters just to bypass a source limit.
