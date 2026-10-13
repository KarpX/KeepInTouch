"""
KeepInTouch: Скрипт переноса данных из JSON в базу данных PostgreSQL (ПР7).
Использует модуль прямого подключения db/database.py, метод executemany() и параметризацию %s.
"""

import json
from pathlib import Path
from db.database import BASE_DIR, get_connection

USERS_FILE = BASE_DIR / "data" / "users.json"
GROUPS_FILE = BASE_DIR / "data" / "groups.json"
CONTACTS_FILE = BASE_DIR / "data" / "contacts.json"


def load_json(filepath: Path):
    """Чтение JSON-файла с кодировкой utf-8."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def import_users(cur):
    """Импорт пользователей из data/users.json."""
    users = load_json(USERS_FILE)
    cur.executemany(
        """
        INSERT INTO auth_user (
            id, username, first_name, last_name, email, password,
            is_active, is_staff, is_superuser, date_joined
        )
        VALUES (%s, %s, %s, %s, %s, '!', TRUE, FALSE, FALSE, CURRENT_TIMESTAMP)
        ON CONFLICT (id) DO UPDATE 
        SET username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            email = EXCLUDED.email;
        """,
        [
            (
                u["id"],
                u.get("username", u["email"].split("@")[0] if "@" in u.get("email", "") else f"user_{u['id']}"),
                u.get("name", "").split()[0] if u.get("name") else "",
                u.get("name", "").split()[1] if u.get("name") and len(u.get("name", "").split()) > 1 else "",
                u.get("email", f"user{u['id']}@example.com"),
            )
            for u in users
        ],
    )
    print(f"Импортировано пользователей: {len(users)}")


def import_groups(cur):
    """Импорт групп контактов из data/groups.json."""
    groups = load_json(GROUPS_FILE)
    cur.executemany(
        """
        INSERT INTO contacts_group (id, name, description, owner_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET name = EXCLUDED.name,
            description = EXCLUDED.description,
            owner_id = EXCLUDED.owner_id;
        """,
        [
            (
                g["id"],
                g["name"],
                g.get("description", ""),
                g.get("owner_id", 1),
            )
            for g in groups
        ],
    )
    print(f"Импортировано групп: {len(groups)}")


def import_contacts(cur):
    """Импорт телефонных контактов из data/contacts.json."""
    contacts = load_json(CONTACTS_FILE)
    cur.executemany(
        """
        INSERT INTO contacts_contact (
            id, name, firstname, number, birthday, is_favorite, tags, owner_id, group_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET name = EXCLUDED.name,
            firstname = EXCLUDED.firstname,
            number = EXCLUDED.number,
            birthday = EXCLUDED.birthday,
            is_favorite = EXCLUDED.is_favorite,
            tags = EXCLUDED.tags,
            owner_id = EXCLUDED.owner_id,
            group_id = EXCLUDED.group_id;
        """,
        [
            (
                c["id"],
                c["name"],
                c.get("firstname", ""),
                int(c["number"]),
                c["birthday"],
                bool(c.get("is_favorite", False)),
                c.get("tags", ""),
                c.get("user_id", 1),
                c.get("group_id"),
            )
            for c in contacts
        ],
    )
    print(f"Импортировано контактов: {len(contacts)}")


def sync_sequences(cur):
    """Синхронизация автоинкрементных последовательностей PostgreSQL."""
    cur.execute("SELECT setval(pg_get_serial_sequence('auth_user', 'id'), COALESCE((SELECT MAX(id) FROM auth_user), 1));")
    cur.execute("SELECT setval(pg_get_serial_sequence('contacts_group', 'id'), COALESCE((SELECT MAX(id) FROM contacts_group), 1));")
    cur.execute("SELECT setval(pg_get_serial_sequence('contacts_contact', 'id'), COALESCE((SELECT MAX(id) FROM contacts_contact), 1));")


def main():
    """Основная функция импорта данных с управлением транзакцией."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            import_users(cur)
            import_groups(cur)
            import_contacts(cur)
            sync_sequences(cur)
        conn.commit()
        print("Импорт данных из JSON в базу данных успешно завершён!")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при импорте данных: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
