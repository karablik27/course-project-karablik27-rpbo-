# Security NFR — BDD Acceptance Scenarios

## Цель
Подтвердить выполнение ключевых нефункциональных требований из `NFR.md`
посредством сценариев приёмки в формате **BDD (Given / When / Then)**.
Сценарии отражают реальные проверки для FastAPI-приложения (CRUD `/objectives`, `/key_results`).

---

## Scenario 1 — Ограничение времени ответа API (NFR-01)

**Feature:** API Performance
**ID:** NFR-01

```gherkin
Scenario: Проверка времени ответа API
  Given работающий FastAPI backend с эндпоинтом /objectives
  When выполняется 1000 GET-запросов с помощью K6
  Then 95-й перцентиль времени ответа не превышает 500 миллисекунд
```

---

## Scenario 2 — Контроль ошибок в ответах (NFR-02)

**Feature:** API Reliability
**ID:** NFR-02

```gherkin
Scenario: Проверка процента ошибок при массовых запросах
  Given работающий backend с CRUD-операциями /key_results
  When выполняется серия из 5000 запросов (GET/POST/PUT/DELETE)
  Then доля HTTP-ошибок 4xx и 5xx не превышает 1% от всех запросов
```

---

## Scenario 3 — Ограничение размера входных данных (NFR-03) — негативный

**Feature:** Request Validation
**ID:** NFR-03

```gherkin
Scenario: Превышение лимита тела запроса
  Given API настроен с ограничением тела запроса 1 МБ
  When пользователь отправляет POST-запрос размером 2 МБ
  Then сервер возвращает 413 Payload Too Large
  And запрос не сохраняется в базе данных
```

---

## Scenario 4 — Обработка исключений (NFR-04)

**Feature:** Centralized Exception Handling
**ID:** NFR-04

```gherkin
Scenario: Исключения логируются централизованно и маскируются для клиента
  Given включено middleware для обработки ошибок
  When при выполнении запроса возникает KeyError
  Then ошибка записывается в файл error.log с уровнем ERROR
  And пользователь получает ответ в формате RFC 7807 без стек-трейса
```

---

## Scenario 5 — Безопасность БД (NFR-05) — негативный

**Feature:** SQL Injection Protection
**ID:** NFR-05

```gherkin
Scenario: Попытка SQL-инъекции не приводит к изменению данных
  Given приложение использует SQLAlchemy ORM
  When злоумышленник отправляет payload "'; DROP TABLE key_results;--"
  Then ORM корректно экранирует ввод
  And данные в таблице key_results остаются без изменений
  And предупреждение записывается в лог безопасности
```

---

## Примечание

Сценарии охватывают ключевые NFR проекта:
- **Производительность (NFR-01)**
- **Надёжность API (NFR-02)**
- **Безопасность ввода и БД (NFR-03, NFR-05)**
- **Корректная обработка ошибок (NFR-04)**

Проверки выполняются через:
- `pytest` и интеграционные тесты,
- нагрузочные тесты K6 / Locust,
- CI-пайплайн (`pytest --cov`, логирование, анализ отчётов).

---

**Связанные документы:**
- [`NFR.md`](./NFR.md)
- [`NFR_TRACEABILITY.md`](./NFR_TRACEABILITY.md)
