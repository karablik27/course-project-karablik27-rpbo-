# ADR-002: Централизованная обработка ошибок в формате RFC 7807

**Дата:** 2025-10-21
**Статус:** Accepted

---

## Context
Клиентам требуется единообразный и безопасный формат ошибок без утечки внутренних деталей/стека.
По умолчанию фреймворк может возвращать текстовые ответы или подробные трейсбеки, что увеличивает риск раскрытия информации (**Information Disclosure**).

Связанные требования и артефакты:
- **NFR-04 — Централизованная обработка ошибок** (issue: #16) — ≥95% ошибок в формате RFC 7807.
- **DFD**: F22–F23 (*ExceptionLogging middleware*), F21–F28 цепочка.
- **Risk Register**: **R3 — Утечка деталей ошибок**; **R8 — Исключения «вешают» пайплайн**.
- **Код**: `app/middleware/errors.py` (логирование в `error.log`, Problem+JSON).
- **Тесты**: `tests/test_errors.py`, `tests/test_exceptions.py`.

---

## Decision
Добавлен middleware **`ExceptionLoggingMiddleware`**, который:
- Оборачивает пайплайн (`BaseHTTPMiddleware.dispatch`), перехватывает необработанные исключения;
- Пишет событие уровня **ERROR** в `error.log` (с `exc_info=True`);
- Возвращает ответ в формате **RFC 7807** (`application/problem+json`), пример:
  ```json
  {
    "type": "about:blank",
    "title": "Internal Server Error",
    "status": 500,
    "detail": "An unexpected error occurred."
  }
  ```

---

## Alternatives
1. **Регистрация `exception_handler` для каждого типа ошибки**.
   **Плюсы:** тонкая настройка. **Минусы:** расползание хэндлеров, сложнее обеспечить ≥95% покрытия.
2. **Вывод stacktrace в ответе при DEBUG**.
   **Минусы:** риск утечек в проде; несоответствие безопасным практикам.
3. **Единый middleware + точечные `exception_handler` там, где нужно** — **компромиссный подход, выбран**.

---

## Consequences / Security impact
- Снижен риск **R3** (information disclosure), **R8** (зависание пайплайна).
- KPI/SLO: доля ответов, удовлетворяющих RFC 7807 (целевое ≥95%), наличие записи события в логе при 5xx.
- DX: клиентам проще обрабатывать ошибки (type/title/status/detail).

---

## Acceptance Criteria (DoD) & Rollout Plan
**DoD:**
- [x] Middleware подключён в `app/main.py` **последним** среди защитных, чтобы ловить всё.
- [x] Логирование ошибок в `error.log` подтверждено.
- [x] Тесты `tests/test_errors.py`, `tests/test_exceptions.py` зелёные.
- [x] Соответствие **NFR-04**, рискам **R3/R8**.

**Rollout:**
- Dev: включено сразу.
- Prod: бездоу́нтаймово; мониторинг частоты 5xx и размера `error.log`.
- При необходимости — обогащение RFC7807 полем `correlation_id` (сохранена совместимость).

---

## Links
- **NFR-04**, issue: #16
- **Threat Model**: DFD (F22–F23/F21–F28), STRIDE/Risks **R3**, **R8**
- **Код**: `app/middleware/errors.py`, `app/main.py`
- **Тесты**: `tests/test_errors.py`, `tests/test_exceptions.py`
- **PR**: `p05-secure-coding → main`
- Feature-flag: `RFC7807_ENABLED` (включает Problem+JSON глобально; на stage можно держать выключенным и включать точечно).
- Pilot: включение флага на 10% инстансов (canary) с мониторингом доли 5xx и размера `error.log`, затем раскатка на 100%.
