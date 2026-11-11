# Study schema v2

Location IDs are in the project-private config/notion.local.json; obtain from hub links if unavailable. Never hardcode this user's IDs in reusable skill files.

Four databases:
- Предмети: Назва (title), Семестр (text), Викладачі (text), Правила здачі and Джерело правил (text), Матеріали (URL), Кінець здачі (date), CIST назви and CIST ID викладачів (text), Архів (checkbox).
- Роботи: Назва; Предмет (relation); Тип; Стан; Залишок год (nullable number); Оцінка (Невідомо/Попередня/Уточнена); Дедлайн + Джерело дедлайну; Потрібен захист; Час здачі год; Учасники й відповідальність; Блокування; Залежить від (self-relation); План; Тиждень фокусу (Monday); Кінець фокусу (Sunday); План год; Пріоритет; Наступний крок; Чому зараз; Ключ імпорту; Операція; Архів; Остання зміна (system last-edited time).
- Можливості здачі: Назва; Предмет and Роботи (relations); Коли (date/time with timezone); Викладач; Група; Підтвердження; Стан; Джерело; Посилання; Перевірено; Умови; Ключ CIST; Операція.
- Тижневі плани: Назва; Тиждень (Monday–Sunday date range); Кінець тижня (Sunday); Стан (Чернетка/Актуальний/Потребує перегляду/Історія); Доступно год; Резерв % (0–100); Заплановано год; Оновлено; Ключ тижня; Операція; Роботи (reverse relation).

Work states: До виконання → У роботі → Готова до здачі → Здана / захищена → Зарахована. Return to У роботі only with actual correction requirements, not canceled attendance. Done coding does not prove submission. Credited means final closure. A task without defense still has actual submission/acceptance semantics.

Opportunity confirmation: Кандидат із розкладу / Допускається правилами / Підтверджена домовленість. State: Майбутня / Скасована / Не відбулася / Завершена. A past time never changes work status. Empty Роботи relation means course-wide candidate, not unconditional acceptance of all work. Record limits in Умови.

Settings are a human-editable page with semester start/end, ordinary self-study hours/week, reserve, timezone, group/schedule identity, electives and current-plan link. Missing values stay unset. End of semester is not automatically copied into task Дедлайн. Per-course final submission cutoff may differ.

Course/task bodies hold rich instructions, material links, specific dependency requirements, collaboration responsibility and a dated change journal. Plan bodies hold recommendations, estimates, assumptions, feasibility warnings, sources and revision snapshots.

## Optional fields introduced during personal onboarding

Роботи also supports `Формат роботи` (Індивідуальна/Групова/Парна), `Напрям` (Навчальна дисципліна/Дипломний проєкт), and `Бажаний період` (date/range). Fetch schema to discover these fields. Format is separate from assignment type. A diploma milestone can have no Предмет relation; do not invent a university subject for it. Desired dates are soft targets, never copy them into Дедлайн. Unset defense checkbox is not evidence that submission needs no defense.

## Course-level personal effort (v2)

Предмети: `Ваші зусилля` SELECT(Невідомо, Мінімальні, Помірні, Значні) and `Примітка до зусиль` text. This assesses active attention while using AI agents and preparing for defense, not code complexity or unattended compute time. Default Невідомо. Never convert categories into hours.

Legacy task fields `Залишок год`, `Оцінка`, `Час здачі год`, `План год` are hidden for compatibility, optional and not the primary planning inputs. New templates omit them. Weekly capacity stays numeric. `Заплановано год` is optional and only represents explicit attention-time allocations, never fabricated task durations.
