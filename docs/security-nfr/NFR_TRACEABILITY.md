# Traceability Matrix: NFR ↔ Stories / Tasks

| Story / Task | Описание                                                   | Связанные NFR | Компонент | Приоритет | Практика (P) | Связь с Issue (тег/номер) | Дата релиза |
|--------------|------------------------------------------------------------|----------------|------------|------------|---------------|---------------------------|-------------|
| S-01 | Настройка репозитория, CI и инженерной гигиены             | NFR-06, NFR-08 | CI / Repo | Medium | **P01 — Repo Hygiene & Bootstrap** | issue: #3 `P01`           | 2025.09     |
| S-02 | Создание ручек, защита main и код-ревью                    | NFR-06, NFR-08 | Git / CI | High | **P02 — Git-процессы и рецензирование** | issue: #5 `P02`           | 2025.10     |
| S-03 | Формулировка измеримых Security NFR и приёмочных сценариев | Все (NFR-01…NFR-08) | Docs / Security NFR | High | **P03 — Security NFR** | issue: #7 `P03`           | 2025.10     |
| S-04 | Построение модели угроз (DFD, STRIDE, Риски)               | NFR-03, NFR-04, NFR-05, NFR-07 | Docs / Threat Model | High | **P04 — Threat Modeling** | issue: #8 `P04`           | 2025.10     |
| S-05 | Архитектурные решения и их реализация (ADR + тесты)        | NFR-04, NFR-05, NFR-06, NFR-07, NFR-08 | Docs / Code / Tests | High | **P05 — Secure Coding & ADR** | issue: #9 `P05`           | 2025.11     |
| S-06 | Безопасное кодирование и негативные тесты                  | NFR-03, NFR-04, NFR-05, NFR-07, NFR-08 | CI / Backend | High | **P06 — Secure Coding (негативные тесты)** | issue: #10 `P06`          | 2025.11     |
| S-07 | Контейнеризация приложения и базовый харднинг              | NFR-01, NFR-02, NFR-06 | Docker / Compose | Medium | **P07 — Container Hardening** | issue: #11 `P07`          | 2025.12     |
| S-08 | Настройка CI/CD конвейера и автоматических проверок        | NFR-01, NFR-02, NFR-06, NFR-08 | CI/CD Pipeline | High | **P08 — CI/CD Minimal** | issue: #12 `P08`          | 2025.12     |
