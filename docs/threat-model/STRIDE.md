# STRIDE Threat Model — OKR Tracker (FastAPI)

**Контекст:** см. `docs/threat-model/DFD.md` (потоки F1–F28, TB1–TB3). Ниже 12 угроз, каждая строка соотнесена 1:1 с риском **R1–R12**.

| Поток/Элемент | Угроза (STRIDE) | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---|---|---|---|---|---|
| **F1 User→API (HTTPS)** | **S: Spoofing** | **R1** | **TLS+HSTS**, строгий **CORS allowlist**, (опц.) статический `X-API-Key` | NFR-07 | Тест CORS (запрет `*`), проверка HSTS/HTTPS на ingress; unit-тест middleware API-key |
| **F24 BodySizeLimit (middleware)** | **D: DoS** | **R2** | Лимит тела **1MB → 413** | NFR-03 | pytest «>1MB → 413»; k6 крупные payload |
| **F22–F23 ExceptionLogging** | **I: Information Disclosure** | **R3** | **RFC7807** без стека; логирование в `error.log` | NFR-04 | Контрактный тест формата ошибки; ручная проверка логов |
| **F12–F20 ORM → DB** | **T / I** | **R4** | Только **SQLAlchemy ORM** (без raw SQL) | NFR-05 | bandit/ruff; review на отсутствие `.execute(sql)` |
| **F3–F11 CRUD-трафик** | **R: Repudiation** | **R5** | **Access-логи** method/path/status | NFR-06 | Проверка трейла в логах (`METHOD path -> status`) |
| **F1 периметр API** | **I: Misconfig (CORS)** | **R6** | **CORS allowlist** (точные Origin’ы, без `*` с credentials) | NFR-07 | e2e из браузера: запрет кросс-доменных запросов; ревью конфигурации CORS |
| **F14/F16/F19 чтение из DB** | **I: Info Disclosure** | **R7** | **response_model** (только whitelisted-поля) | NFR-07 | Тест сериализации ответа |
| **F21–F28 цепочка middleware** | **D: DoS** | **R8** | try/except; **500 Problem+JSON**; нет рекурсии | NFR-04 | Тест «искусственное исключение → 500 + лог» |
| **F6–F9 массовые модификации** | **D: Abuse** | **R9** | **Rate-limit** на IP/токен для POST/PUT/DELETE | NFR-02, NFR-03 | k6 негативные сценарии → **429** |
| **F3–F11 под нагрузкой** | **D: Perf** | **R10** | Оптимизация; p95 ≤ 500ms | NFR-01 | Отчёт k6/Locust p95 |
| **F3–F11 bulk-чтение** | **I/D: No pagination/limits** | **R11** | **Пагинация**, `limit`/`max_limit`, защитные капы | NFR-03 | e2e: лимит выдачи ≤ max_limit; k6 подтверждает |
| **F3–F11 перечисление id** | **D/I: Enumeration** | **R12** | **Rate-limit** на GET by id; **единые ответы** для чужого/несущ. id | NFR-02, NFR-03 | k6 негативные сценарии (429); e2e на поведение 404 |

---

## Привязка к коду (evidence)
- **Middleware**
  - `app/middleware/limits.py` — `BodySizeLimitMiddleware` (413 для >1MB).
  - `app/middleware/errors.py` — `ExceptionLoggingMiddleware` (RFC7807 + error.log).
- **Роутеры**
  - `routers/objectives.py` — CRUD целей, проверки через Pydantic и бизнес‑правила.
  - `routers/key_results.py` — CRUD ключевых результатов, валидация и ограничения.
- **DB слой**
  - `app/db.py`, `app/models.py` — SQLAlchemy ORM, каскад для FK.