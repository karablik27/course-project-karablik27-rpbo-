# ADR-003: Защита периметра API (X-API-Key) и принудительный HTTPS (HSTS)

**Дата:** 2025-10-21
**Статус:** Accepted

---

## Context
На периметре edge‑API необходимо ограничить неавторизованные **модифицирующие** запросы и
заставить браузеры использовать защищённый транспорт (**HTTPS**).
Также требуется корректная работа CORS‑preflight.

Связанные требования и артефакты:
- **Threat Model**: TB1 (HTTP boundary), **F1** (User→API), см. `docs/threat-model/DFD.md`.
- **Risk Register**: **R1 — Подмена клиента/злоупотребление анонимным доступом**, **R2 — MITM/перехват** (см. HSTS часть в R1).
- **NFR**: косвенно связано с **NFR-06** (логирование), **NFR-07** (валидация ввода/CORS‑allowlist).
- **Код**: `app/middleware/security.py` (ApiKeyGate + HSTS), `app/main.py` (CORS).
- **Тесты**: `tests/test_r1_api_key_gate.py`, `tests/test_r1_cors_hsts.py`.

---

## Decision
1. **API‑ключ для write‑методов**
   Middleware **`ApiKeyGateMiddleware`** требует заголовок `X-API-Key` для `POST/PUT/PATCH/DELETE`,
   если ключ задан через `app.state.API_EDGE_KEY` или `API_EDGE_KEY` (env).
   Сравнение через `hmac.compare_digest` (устойчиво к timing attacks).
   При отсутствии/ошибке — `401` с **Problem+JSON** и заголовком `WWW-Authenticate: ApiKey`.

2. **Принудительный HTTPS через HSTS**
   Middleware **`HSTSMiddleware`** добавляет `Strict-Transport-Security: max-age=15552000; includeSubDomains[; preload]`.
   Проверяется юнит‑тестом; в проде заголовок устанавливается на TLS‑входе (дублирование на ingress).

3. **CORS allowlist**
   `CORSMiddleware` сконфигурирован через env `ALLOWED_ORIGINS` (без `*` при credentials).
   Preflight `OPTIONS` разрешён для доверенных Origin’ов.

---

## Alternatives
1. **OAuth2/JWT**.
   **Плюсы:** полнофункциональная аутентификация. **Минусы:** избыточно для edge‑ограничений, требует state/refresh.
2. **BasicAuth**.
   **Минусы:** постоянная передача секрета, риск перехвата при ошибках конфигурации TLS.
3. **Отсутствие HSTS**.
   **Минусы:** downgrade‑атаки, микс‑контент.
4. **Выбранный компромисс**: **X-API-Key + HSTS + строгий CORS** для простого периметра;
   миграция на OAuth2/JWT возможна позже без ломающего изменения публичного контракта.

---

## Consequences / Security impact
- Снижен риск **R1** (неавторизованный доступ) и **R2** (MITM).
- Метрики: доля отказов **401** без ключа; доля корректных preflight‑ответов для `ALLOWED_ORIGINS`.
- Совместимость: ключ включается «на лету» через `app.state` (как в тестах), не требует рестарта.

---

## Acceptance Criteria (DoD) & Rollout Plan
**DoD:**
- [x] `ApiKeyGateMiddleware` и `HSTSMiddleware` подключены в `app/main.py`.
- [x] Тесты `tests/test_r1_api_key_gate.py`, `tests/test_r1_cors_hsts.py` зелёные.
- [x] CORS‑список задаётся через `ALLOWED_ORIGINS`; проверка preflight.

**Rollout:**
- Dev: ключ выключен по умолчанию (нет `API_EDGE_KEY`), включение — через `app.state`.
- Stage: включаем ключ для write‑методов; проверяем интеграцию фронта.
- Prod: ключ в env, TLS на ingress, **HSTS** включён; **canary** 10% → 100%.
- Документация: README секция «Security/Edge», обновление шаблонов запросов в коллекции.

---

## Links
- **Threat Model**: DFD (F1, TB1), STRIDE **R1/R2**
- **NFR**: NFR‑06 (логи), NFR‑07 (валидация/CORS)
- **Код**: `app/middleware/security.py`, `app/main.py`
- **Тесты**: `tests/test_r1_api_key_gate.py`, `tests/test_r1_cors_hsts.py`
- **PR**: `p05-secure-coding → main`
- Feature-flag: включение API-gate происходит наличием `API_EDGE_KEY` (app.state/env).
- Canary: ставим `API_EDGE_KEY` только на 10% инстансов (только для write-методов), затем 100%.
- HSTS-параметры: `HSTS_MAX_AGE`, `HSTS_INCLUDE_SUBDOMAINS`, `HSTS_PRELOAD` через env — для безопасного пилота.
