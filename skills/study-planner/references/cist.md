# Official CIST adapter

Use only the official university CIST. Do not use Mindenit, its libraries, proxies or derived schedules. Verified on 2026-11-11; runtime results, not this document, establish future availability.

Standard-library helper: `python3 <skill-directory>/scripts/cist.py lookup-group '<ваша група>'` resolves exact name in the official directory. Read group identity from personal settings; never use another student's ID by default.

Fetch: `python3 <skill-directory>/scripts/cist.py fetch --kind group --id GROUP_ID --from 2026-11-09 --to 2026-11-15 --output data/cist/group.json`. The dates illustrate the required format. GROUP_ID must come from the recipient’s verified directory lookup; no personal group is preconfigured. Pass actual requested dates. For teacher use --kind teacher and the officially verified teacher ID. Resolve teacher through official CIST page and its `IAS_ADD_Teach_in_List` links; do not guess IDs, scrape third-party datasets or reuse a name match without confirming identity/department.

The official `/i/ias/css/ias.js` defines CSV GET requests:
- Group: `WEB_IAS_TT_GNR_RASP.GEN_GROUP_POTOK_RASP?ATypeDoc=3&Aid_group=ID&Aid_potok=0&ADateStart=DD.MM.YYYY&ADateEnd=DD.MM.YYYY&AMultiWorkSheet=0`
- Teacher: `WEB_IAS_TT_GNR_RASP.GEN_TEACHER_KAF_RASP?ATypeDoc=3&Aid_sotr=ID&Aid_kaf=0&ADateStart=DD.MM.YYYY&ADateEnd=DD.MM.YYYY&AMultiWorkSheet=0`

Base `https://cist2.nure.ua/ias/app/tt/`. CSV requests verified without login/cookies. Directory pages need a cookie jar to avoid session redirect loops. Windows-1251 CSV uses CR line endings and 13 Outlook-style columns. No API key or third-party package is used. There is no verified availability SLA or published request quota: fetch a bounded relevant period on request, not aggressive polling.

The helper returns source URL, fetched-at timestamp, checksum, original fields, stable lesson keys and timezone-aware dates. It rejects HTML errors, unknown headers, wrong field counts and out-of-range dates. A header-only file is a valid empty result, not proof of canceled classes. Error never overwrites an earlier cache. Cache is disposable evidence; Notion remains the source of task truth. No destructive sync: disappearance from a new CSV is a change to review, not permission to erase a manually confirmed opportunity.

Do not fabricate missing teacher/subject/group IDs: CSV includes descriptive titles and may not contain all metadata. Different electives can overlap in the group export. Match user-confirmed CIST course aliases; ask once about unmapped electives and retain their uncertainty. Group and teacher exports can show the same class with different wording; deduplicate by date/time plus verified course/teacher/group, not title alone. Stable keys are scoped to export identity and are NOT guaranteed cross-export IDs.

Store only relevant opportunities in Notion with `Ключ CIST`, source, checked-at date and confirmation `Кандидат із розкладу` unless separate course rules/agreement establish more. Refresh candidate dates from CIST while preserving human confirmations/cancellations as separate evidence. Do not overwrite a user-reported instructor absence with a timetable entry. Keep a dated journal if the two sources disagree.

When a course permits defense with other groups, check the exact course AND the user's relevant lab/practical instructor. A matching course taught by a different instructor, or merely its lecturer, does not establish eligibility. Keep lab and practical instructor identities separate where they differ. If identities are unknown, keep the event a candidate rather than inventing a confirmed opportunity.

## Resolve the user's actual lab/practical teachers

`python3 <skill-directory>/scripts/cist.py teaching --id GROUP_ID --from YYYY-MM-DD --to YYYY-MM-DD --output data/cist/teaching.json` reads the official HTML export (`ATypeDoc=1`). Its footer contains subject IDs/aliases, separate lecture/practical/lab assignments, groups and linked teacher IDs. Use a semester-sized period so roles not taught this week are included. Match the user's selected elective stream before accepting an assignment. Preserve separate role mappings in course `CIST ID викладачів`, e.g. JSON object with `Лб` and `Пз` arrays. Never pick a lecturer just because the subject matches. The source URL and checked-at date belong with the mapping; manual user correction overrides stale timetable metadata. This reader was tested against the official group export and a fixture with three different instructors for the three roles.
