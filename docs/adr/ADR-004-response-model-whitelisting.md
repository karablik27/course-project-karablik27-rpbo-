# ADR-004: Whitelisting ответа через `response_model` (защита от утечек данных)

**Дата:** 2025-10-21
**Статус:** Accepted

---

## Context
В ответах API запрещено возвращать служебные/внутренние поля модели.
Для предотвращения утечек данных (PII/служебные ключи) используется whitelisting полей через `response_model` (Pydantic).

Связанные требования и артефакты:
- **NFR-07 — Валидация пользовательского ввода/вывода** (issue: #19).
- **DFD**: F14/F16/F19 (чтение из БД и сериализация), TB1 (HTTP boundary).
- **Risk Register**: **R7 — Лишние поля в ответах (утечка служебных данных)**.
- **Код**: `app/schemas.py` (Pydantic-модели), `app/routers/objectives.py`, `app/routers/key_results.py` (параметр `response_model`).
- **Тест**: `tests/test_p05_extra_1.py` (новый).

---

## Decision
Стандартизировать выдачу всех GET/POST/PUT эндпоинтов через явный `response_model=...`.
- Для Objectives → `Objective` (id, title, description, isComplete);
- Для KeyResults → `KeyResult` (id, title, target_value, current_value, objective_id).
Внутренние поля в запросе игнорируются и **не попадают** в ответ.

---

## Alternatives
1. **Без `response_model` (raw dict/ORM)**.
   **Минусы:** легко протечь служебным полям; высокая цена ревью.
2. **Глобальный сериализатор** с фильтрацией.
   **Плюсы:** единое место контроля; **Минусы:** сложнее поддерживать типобезопасность.
3. **Выбранный путь** — `response_model` на каждом маршруте (прозрачно, типобезопасно, просто тестировать).

---

## Consequences / Security impact
- Снижен риск **R7** (утечки).
- Поддерживается инвариант: «в ответе только whitelisted-поля».
- Клиенты получают стабильный контракт (схемы совпадают с OpenAPI).

---

## Acceptance Criteria (DoD) & Rollout Plan
**DoD:**
- [x] Все публичные эндпоинты имеют `response_model`.
- [x] `tests/test_p05_extra_1.py` — зелёный.
- [x] Линтер/ревью запрещает добавлять эндпоинты без `response_model`.

**Rollout:**
- **Feature-flag:** `RESPONSE_MODEL_POLICY` ∈ {`off`, `warn`, `enforce`} (по умолчанию — `warn`).
  На `warn` приложение **не падает**, но при старте выполняется проверка маршрутов и логируются предупреждения для любой ручки без `response_model`.
  На `enforce` приложение **не стартует**, если найдены публичные эндпоинты без `response_model`.
- **Pilot:** на **stage** — `RESPONSE_MODEL_POLICY=warn` (1 спринт), наблюдаем логи предупреждений. На **prod** — переключаем на `enforce` после исправления всех замечаний.
- **Rollback:** вернуть `RESPONSE_MODEL_POLICY=off` (отключить проверку) при необходимости быстрого восстановления.

---

## Links
- **NFR-07**, issue: #19
- **Threat Model**: DFD (F14/F16/F19), Risk **R7**
- **Код**: `app/schemas.py`, `app/routers/objectives.py`, `app/routers/key_results.py`
- **Тест**: `tests/test_p05_extra_1.py`
- **PR**: `p05-secure-coding → main`
