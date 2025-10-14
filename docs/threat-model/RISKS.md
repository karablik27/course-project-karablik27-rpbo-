# Risk Register — OKR Tracker (FastAPI)

Связано с: `docs/threat-model/DFD.md` (F1–F28), `docs/threat-model/STRIDE.md` (таблица STRIDE), NFR из P03.

| RiskID | Описание | Связь (F/NFR) | L | I | Risk | Стратегия | Владелец | Срок | Критерий закрытия |
|---|---|---|---|---|---|---|---|---|---|
| **R1** | Подмена клиента/злоупотребление анонимным доступом на периметре | F1, NFR-07 | 3 | 4 | 12 | Снизить | @backend | 2025-10-20 | **TLS+HSTS**, **CORS allowlist**, (опц.) middleware `X-API-Key`; e2e CORS тест |
| **R2** | Перегрузка большим телом (DoS) | F24, NFR-03 | 2 | 4 | 8 | Снизить | @backend | 2025-10-18 | pytest «>1MB → 413»; k6 с большими payload |
| **R3** | Утечка деталей ошибок | F22–F23, NFR-04 | 2 | 5 | 10 | Снизить | @backend | 2025-10-23 | RFC7807 без stacktrace; контрактные тесты |
| **R4** | SQL-инъекция / несогласованное изменение | F12–F20, NFR-05 | 2 | 5 | 10 | Избежать | @backend | 2025-10-25 | bandit/ruff в CI; отсутствие raw SQL в PR |
| **R5** | Repudiation: спор действий пользователя | F3–F11, NFR-06 | 3 | 3 | 9 | Снизить | @backend | 2025-10-22 | Access-логи method/path/status; проверка трейлов |
| **R6** | CORS-misconfig: кросс-доменные браузерные вызовы к API | F1, NFR-07 | 3 | 4 | 12 | Снизить | @backend | 2025-10-21 | Строгий **CORS allowlist**; e2e из фронта — запросы с чужого Origin блокируются |
| **R7** | Лишние поля в ответах (утечка служебных данных) | F14/F16/F19, NFR-07 | 2 | 4 | 8 | Снизить | @backend | 2025-10-19 | `response_model` везде; тест сериализации |
| **R8** | Исключения «вешают» пайплайн (DoS) | F21–F28, NFR-04 | 2 | 4 | 8 | Снизить | @backend | 2025-10-21 | Тест: искусств. исключение → 500 Problem+JSON + запись в лог |
| **R9** | Массовые модификации без ограничений | F6–F9; NFR-02, NFR-03 | 3 | 4 | 12 | Снизить | @backend | 2025-10-28 | Включён **rate-limit**; k6 негативные сценарии → 429 |
| **R10** | p95 > 500ms под нагрузкой | F3–F11; NFR-01 | 2 | 3 | 6 | Снизить | @backend | 2025-10-29 | Отчёт k6/Locust: **p95 ≤ 500ms** |
| **R11** | Нет пагинации/лимитов → массовая выгрузка | F3–F11; NFR-03 | 3 | 3 | 9 | Снизить | @backend | 2025-10-26 | Пагинация и `max_limit`; e2e подтверждает ограничение выдачи |
| **R12** | Перечисление/сканирование id (enum) | F3–F11; NFR-02, NFR-03 | 3 | 4 | 12 | Снизить | @backend | 2025-10-28 | Rate-limit на GET by id; **единый ответ** для чужого/несущ. id; k6 → 429 |

## Легенда
- **L** — вероятность (1–5), **I** — ущерб (1–5), **Risk = L×I**.
- **Стратегии**: Избежать / Снизить / Принять / Передать.
- Связь указывает **потоки F** из DFD и **NFR** из P03.

## Ссылки на Issues
- [R1](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/22)
- [R2](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/23)
- [R3](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/24)
- [R4](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/25)
- [R5](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/26)
- [R6](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/27)
- [R7](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/28)
- [R8](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/29)
- [R9](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/30)
- [R10](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/31)
- [R11](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/32)
- [R12](https://github.com/hse-secdev-2025-fall/course-project-karablik27/issues/33)
