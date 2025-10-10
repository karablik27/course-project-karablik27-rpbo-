import re
from pathlib import Path


def test_no_raw_sql_usage():
    """NFR-05: Проверка отсутствия прямых SQL-запросов (исключая ORM API)"""
    src_dir = Path("app")

    # Паттерн только на настоящие SQL-строки, не совпадающие с ORM-функциями
    raw_sql_pattern = re.compile(
        r'\.execute\s*\(\s*["\']\s*(SELECT|INSERT|DELETE|UPDATE)', re.IGNORECASE
    )

    bad_files = []

    for file in src_dir.rglob("*.py"):
        if file.name == "__init__.py":
            continue

        text = file.read_text(encoding="utf-8")

        # Пропускаем безопасные импорты ORM
        if "from sqlalchemy" in text or "sqlalchemy.orm" in text:
            pass

        # Проверяем на реальные SQL-строки
        if raw_sql_pattern.search(text):
            bad_files.append(file)

    assert not bad_files, f"Найден raw SQL в файлах: {bad_files}"
