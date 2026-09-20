from datetime import date
from typing import Optional

from .groups import Group
from .users import User


class Contact:

    def __init__(
        self,
        contact_id: int,
        name: str,
        firstname: str,
        number: int,
        birthday: str,
        user: User,
        group: Group,
        is_favorite: bool = False,
    ) -> None:
        self.id = contact_id
        self.name = name
        self.firstname = firstname
        self.number = number
        self.birthday = birthday
        self.user = user
        self.group = group
        self.is_favorite = is_favorite

    def __str__(self) -> str:
        fav = "Да" if self.is_favorite else "Нет"
        return (
            f"ID: {self.id}\n"
            f"Имя: {self.name}\n"
            f"Фамилия: {self.firstname}\n"
            f"Номер: {self.number}\n"
            f"Дата рождения: {self.birthday}\n"
            f"Группа: {self.group.name}\n"
            f"Владелец: {self.user.name}\n"
            f"Избранный: {fav}"
        )

    def toggle_favorite(self) -> None:
        self.is_favorite = not self.is_favorite

    def matches(self, query: str) -> bool:
        q = query.lower()
        return (
            q in self.name.lower()
            or q in self.firstname.lower()
            or q in str(self.number)
            or q in self.group.name.lower()
        )


def add_contact(
    contacts: list[Contact],
    name: str,
    firstname: str,
    number: int,
    birthday: date,
    user: User,
    group: Group,
    is_favorite: bool = False,
) -> Contact:
    new_id = max([c.id for c in contacts], default=0) + 1
    contact = Contact(
        contact_id=new_id,
        name=name,
        firstname=firstname,
        number=number,
        birthday=birthday.isoformat(),
        user=user,
        group=group,
        is_favorite=is_favorite,
    )
    contacts.append(contact)
    return contact


def find_contact_by_id(
    contacts: list[Contact], contact_id: int
) -> Optional[Contact]:
    for c in contacts:
        if c.id == contact_id:
            return c
    return None


def delete_contact(contacts: list[Contact], contact_id: int) -> bool:
    contact = find_contact_by_id(contacts, contact_id)
    if contact is not None:
        contacts.remove(contact)
        return True
    return False


def get_favorite_contacts(contacts: list[Contact]) -> list[Contact]:
    return [c for c in contacts if c.is_favorite]


def search_contacts(contacts: list[Contact], query: str) -> list[Contact]:
    return [c for c in contacts if c.matches(query)]


def sort_contacts_by_name(contacts: list[Contact]) -> list[Contact]:
    return sorted(
        contacts, key=lambda c: (c.name.lower(), c.firstname.lower())
    )