# SCA Summary Report

**Generated from:** SBOM (CycloneDX 1.6) + Grype 0.104.1
**Scan Time:** 2025-12-01 18:45 UTC
**Project:** FastAPI backend

---

## Общее состояние безопасности

| Severity              | Count |
|-----------------------|-------|
| Critical           | 0     |
| High               | 0     |
| Medium             | 0     |
| Low                | 0     |
| Negligible / Unknown | 0   |

**Уязвимостей не обнаружено.**
Это означает:

- Все версии библиотек, включая `fastapi`, `uvicorn`, `sqlalchemy`, `python-multipart`, находятся в безопасных состояниях.
- База данных Grype актуальна на момент сканирования.
- В SBOM нет конфликтующих CPE.

---

## Используемые ключевые зависимости

### Prod

- `fastapi==0.112.2`
- `uvicorn==0.30.5`
- `sqlalchemy==2.0.43`
- `python-multipart==0.0.18` *(обновлено до версии с фиксами)*

### Dev

- `pytest`
- `bandit`
- `black`
- `pre-commit`
- `mypy`
- `ruff`

---

## Remediation status

###  Выполнено

- `python-multipart` обновлён до `0.0.18` — версия без известных CVE.
- Новые зависимости пересканированы по цепочке **SBOM → SCA** → уязвимостей не выявлено.

### Проверки

- Совместимость FastAPI с `python-multipart 0.0.18` — **OK**.
- Работа загрузки файлов и форм — **OK**.
- Breaking changes в changelog библиотеки — **не обнаружено**.

---

## Итоговая оценка проекта

Проект в текущей конфигурации **безопасен**.
SCA не нашёл ни одного CVE во всех зависимостях — текущее состояние можно считать **хорошим с точки зрения безопасности**.

### Рекомендации

- Автоматически обновлять SBOM и SCA в CI при каждом пуше в `main`.
- Проводить регулярный SCA-скан (минимум раз в неделю), так как база уязвимостей обновляется ежедневно.

---

## Metadata

- **SBOM generator:** Anchore Syft `1.38.0`
- **SCA tool:** Grype `0.104.1`
- **Vuln DB:** `vulnerability-db_v6.1.3` (2025-12-01)
- **Scan scope:**
  - `requirements.txt`
  - `requirements-dev.txt`
  - GitHub Actions (workflow actions: `actions/cache`, `actions/checkout`, `actions/setup-python`, `actions/upload-artifact`, `aquasecurity/trivy-action`, `hadolint/hadolint-action`)
