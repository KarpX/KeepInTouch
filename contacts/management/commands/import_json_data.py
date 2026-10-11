import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from contacts.models import Group, Contact
from django.conf import settings


class Command(BaseCommand):
    help = "Импортирует данные из data/*.json в PostgreSQL"

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"

        users_file = data_dir / "users.json"
        groups_file = data_dir / "groups.json"
        contacts_file = data_dir / "contacts.json"

        if not users_file.exists():
            self.stderr.write(self.style.ERROR(f"Файл {users_file} не найден!"))
            return

        self.stdout.write("Начинаем импорт данных...")

        # 1. Импорт пользователей
        user_map = {}
        with open(users_file, "r", encoding="utf-8") as f:
            users_data = json.load(f)

        for u in users_data:
            full_name = u["name"].strip()
            # логин из латинского префикса email или транслита
            username = u["email"].split("@")[0].lower()
            email = u["email"].strip()

            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            if created:
                user.set_password("changeme123")
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [+] Создан пользователь: {username} (пароль: changeme123, email: {email})"
                    )
                )
            else:
                self.stdout.write(f"  [=] Пользователь уже существует: {username}")

            user_map[u["id"]] = user

        # Основной владелец по умолчанию (первый импортированный пользователь)
        default_owner = next(iter(user_map.values()), None)

        # 2. Импорт групп
        group_map = {}
        if groups_file.exists():
            with open(groups_file, "r", encoding="utf-8") as f:
                groups_data = json.load(f)

            for g in groups_data:
                group, created = Group.objects.get_or_create(
                    name=g["name"].strip(),
                    owner=default_owner,
                    defaults={"description": g.get("description", "").strip()},
                )
                group_map[g["id"]] = group
                status_str = "Создана" if created else "Уже существует"
                self.stdout.write(f"  [+] Группа: {group.name} ({status_str})")

        # 3. Импорт контактов
        if contacts_file.exists():
            with open(contacts_file, "r", encoding="utf-8") as f:
                contacts_data = json.load(f)

            for c in contacts_data:
                owner = user_map.get(c.get("user_id"), default_owner)
                group = group_map.get(c.get("group_id"))

                contact, created = Contact.objects.get_or_create(
                    name=c["name"].strip(),
                    firstname=c["firstname"].strip(),
                    owner=owner,
                    defaults={
                        "number": c["number"],
                        "birthday": c["birthday"],
                        "group": group,
                        "is_favorite": c.get("is_favorite", False),
                        "tags": c.get("tags", ""),
                    },
                )
                status_str = "Создан" if created else "Уже существует"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [+] Контакт: {contact.name} {contact.firstname} (тел: {contact.number}) ({status_str})"
                    )
                )

        self.stdout.write(self.style.SUCCESS("✓ Все данные успешно перенесены в PostgreSQL!"))
