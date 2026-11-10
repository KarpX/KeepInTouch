"""
KeepInTouch: Скрипт инспекции структуры базы данных (ПР9, подраздел 5.8.1).
Исследует таблицы, столбцы, типы данных, первичные ключи и количество записей.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from db.database import get_connection


def main():
    print("=" * 60)
    print("KeepInTouch: Инспекция структуры базы данных")
    print("=" * 60)

    try:
        conn = get_connection()
    except Exception as exc:
        print(f"Ошибка подключения к базе данных: {exc}")
        return

    try:
        with conn.cursor() as cur:
            # Получаем список пользовательских таблиц
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row["table_name"] for row in cur.fetchall()]

            print(f"Найдено пользовательских таблиц: {len(tables)}")

            for table_name in tables:
                print(f"\nТаблица: {table_name}")

                # Получаем информацию о столбцах таблицы
                cur.execute("""
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable, 
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public' 
                      AND table_name = %s
                    ORDER BY ordinal_position;
                """, [table_name])
                columns = cur.fetchall()

                # Получаем информацию о первичном ключе
                cur.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                      AND tc.table_name = %s;
                """, [table_name])
                pk_rows = cur.fetchall()
                pk_cols = {r["column_name"] for r in pk_rows}

                print("Столбцы:")
                for col in columns:
                    is_pk = " [PRIMARY KEY]" if col["column_name"] in pk_cols else ""
                    print(
                        f"  - имя={col['column_name']}, "
                        f"тип={col['data_type']}, "
                        f"NULL={'YES' if col['is_nullable'] == 'YES' else 'NO'}"
                        f"{is_pk}"
                    )

                # Подсчитываем количество записей
                cur.execute(f'SELECT COUNT(*) AS cnt FROM "{table_name}"')
                count = cur.fetchone()["cnt"]
                print(f"Количество записей: {count}")

        print("\n" + "=" * 60)
        print("Инспекция структуры базы данных успешно завершена.")
        print("=" * 60)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
