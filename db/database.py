"""
KeepInTouch: Модуль прямого подключения к базе данных PostgreSQL (ПР7).
Обеспечивает работу с базой данных без использования Django ORM.
"""

import os
from pathlib import Path
import psycopg
from psycopg.rows import dict_row

# Корневой каталог проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных окружения из .env (если есть)
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

DB_NAME = os.environ.get("DB_NAME", "keepintouch")
DB_USER = os.environ.get("DB_USER", "kit_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "kit_pass")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5433")


def get_connection():
    """
    Создает и возвращает прямое соединение с базой данных PostgreSQL.
    Настраивает row_factory=dict_row для именованного доступа к полям строк.
    """
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        row_factory=dict_row,
    )
    return conn


def execute_script_file(script_path: str | Path) -> None:
    """Выполняет SQL-скрипт из указанного файла."""
    path = Path(script_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
