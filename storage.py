import json
import os
from typing import Tuple

from models import Contact, Group, User
from models.groups import find_group_by_id
from models.users import find_user_by_id


def load_all_data(
    users_path: str, groups_path: str, contacts_path: str
) -> Tuple[list[User], list[Group], list[Contact]]:
    users: list[User] = []
    groups: list[Group] = []
    contacts: list[Contact] = []

    if os.path.exists(users_path):
        try:
            with open(users_path, "r", encoding="utf-8") as f:
                users_data = json.load(f)
                users = [User.from_data(u) for u in users_data]
        except (json.JSONDecodeError, OSError, KeyError):
            users = []

    if os.path.exists(groups_path):
        try:
            with open(groups_path, "r", encoding="utf-8") as f:
                groups_data = json.load(f)
                groups = [Group.from_data(g) for g in groups_data]
        except (json.JSONDecodeError, OSError, KeyError):
            groups = []

    if os.path.exists(contacts_path):
        try:
            with open(contacts_path, "r", encoding="utf-8") as f:
                contacts_data = json.load(f)
                for item in contacts_data:
                    user_obj = find_user_by_id(users, item["user_id"])
                    group_obj = find_group_by_id(groups, item["group_id"])
                    if user_obj is not None and group_obj is not None:
                        contact = Contact(
                            contact_id=item["id"],
                            name=item["name"],
                            firstname=item["firstname"],
                            number=item["number"],
                            birthday=item["birthday"],
                            user=user_obj,
                            group=group_obj,
                            is_favorite=item.get("is_favorite", False),
                        )
                        contacts.append(contact)
        except (json.JSONDecodeError, OSError, KeyError):
            contacts = []

    return users, groups, contacts


def save_all_data(
    users_path: str,
    groups_path: str,
    contacts_path: str,
    users: list[User],
    groups: list[Group],
    contacts: list[Contact],
) -> None:
    for path in (users_path, groups_path, contacts_path):
        folder = os.path.dirname(path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

    with open(users_path, "w", encoding="utf-8") as f:
        json.dump(
            [{"id": u.id, "name": u.name, "email": u.email} for u in users],
            f,
            ensure_ascii=False,
            indent=2,
        )

    with open(groups_path, "w", encoding="utf-8") as f:
        json.dump(
            [
                {"id": g.id, "name": g.name, "description": g.description}
                for g in groups
            ],
            f,
            ensure_ascii=False,
            indent=2,
        )

    with open(contacts_path, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "id": c.id,
                    "name": c.name,
                    "firstname": c.firstname,
                    "number": c.number,
                    "birthday": c.birthday,
                    "user_id": c.user.id,
                    "group_id": c.group.id,
                    "is_favorite": c.is_favorite,
                }
                for c in contacts
            ],
            f,
            ensure_ascii=False,
            indent=2,
        )