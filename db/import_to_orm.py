"""
KeepInTouch: Скрипт безопасного переноса и актуализации данных через Django ORM (ПР9, подраздел 5.8.2).
Читает данные и синхронизирует их с моделями Django посредством update_or_create() в рамках транзакции.
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

# Определяем корневой каталог проекта KeepInTouch
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Настройка переменной окружения Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keep_in_touch.settings")

# Инициализируем Django
import django
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from contacts.models import Group, Contact


USERS_FILE = BASE_DIR / "data" / "users.json"
GROUPS_FILE = BASE_DIR / "data" / "groups.json"
CONTACTS_FILE = BASE_DIR / "data" / "contacts.json"


def load_json(filepath: Path):
    if not filepath.exists():
        raise FileNotFoundError(f"Файл данных не найден: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 60)
    print("KeepInTouch: Перенос и синхронизация данных через Django ORM")
    print("=" * 60)

    users_data = load_json(USERS_FILE)
    groups_data = load_json(GROUPS_FILE)
    contacts_data = load_json(CONTACTS_FILE)

    # Выполняем запись в целевую базу данных одной атомарной транзакцией
    with transaction.atomic():
        # 1. Сначала переносим пользователей (независимая сущность)
        print("Синхронизация пользователей (User)...")
        for u in users_data:
            full_name = u.get("name", "").strip()
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            email = u.get("email", "").strip()
            username = u.get("username") or (email.split("@")[0].lower() if "@" in email else f"user_{u['id']}")

            user, created = User.objects.update_or_create(
                pk=u["id"],
                defaults={
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "is_active": True,
                },
            )
            # Устанавливаем пароль только для вновь создаваемых записей
            if created or not user.has_usable_password():
                user.set_password("changeme123")
                user.save(update_fields=["password"])

        # 2. Переносим группы контактов (зависят от User)
        print("Синхронизация групп контактов (Group)...")
        # Дефолтный владелец — первый пользователь
        default_owner = User.objects.first()

        for g in groups_data:
            owner_id = g.get("owner_id")
            owner = User.objects.filter(pk=owner_id).first() if owner_id else default_owner

            Group.objects.update_or_create(
                pk=g["id"],
                defaults={
                    "name": g["name"].strip(),
                    "description": g.get("description", "").strip(),
                    "owner": owner,
                },
            )

        # 3. Переносим контакты (зависят от User и Group)
        print("Синхронизация телефонных контактов (Contact)...")
        for c in contacts_data:
            owner_id = c.get("user_id") or c.get("owner_id")
            owner = User.objects.filter(pk=owner_id).first() if owner_id else default_owner

            group_id = c.get("group_id")
            group = Group.objects.filter(pk=group_id).first() if group_id else None

            # Преобразуем строку даты ISO (YYYY-MM-DD) в объект date
            bday_raw = c["birthday"]
            if isinstance(bday_raw, str):
                bday_date = date.fromisoformat(bday_raw)
            else:
                bday_date = bday_raw

            Contact.objects.update_or_create(
                pk=c["id"],
                defaults={
                    "name": c["name"].strip(),
                    "firstname": c.get("firstname", "").strip(),
                    "number": int(c["number"]),
                    "birthday": bday_date,
                    "is_favorite": bool(c.get("is_favorite", False)),
                    "tags": c.get("tags", "").strip(),
                    "owner": owner,
                    "group": group,
                },
            )

    print("\nПеренос данных через Django ORM успешно завершён.")
    print(f"Пользователей: {User.objects.count()}")
    print(f"Групп:         {Group.objects.count()}")
    print(f"Контактов:     {Contact.objects.count()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
