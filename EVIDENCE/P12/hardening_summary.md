# P12 — Hardening summary

## Dockerfile

**До:**
- контейнер запускался от root;
- отсутствовало явное разделение build/runtime стадий.

**После:**
- контейнер запускается от non-root пользователя (`appuser`);
- используется multi-stage build (builder + runtime);
- минимизирован набор пакетов в runtime-образе;
- включён healthcheck.

## Kubernetes (IaC)

**До:**
- отсутствовали ограничения безопасности на pod/container уровне.

**После:**
- включён `runAsNonRoot`;
- задан `runAsUser` / `runAsGroup`;
- отключено `allowPrivilegeEscalation`;
- сброшены все Linux capabilities;
- включён `readOnlyRootFilesystem`;
- используется `seccompProfile: RuntimeDefault`.

## Итог

Применены базовые и расширенные меры харднинга контейнера и Kubernetes-манифестов,
что снижает поверхность атаки и повышает безопасность запуска сервиса.
