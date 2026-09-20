from datetime import date
from models.users import User
from models.groups import Group
from models.contacts import (
    Contact,
    add_contact,
    delete_contact,
    get_favorite_contacts,
    search_contacts,
    sort_contacts_by_name,
)


def test_contact_creation_and_association() -> None:
    user = User(1, "Максим", "m@ex.com")
    group = Group(1, "Друзья", "Круг общения")
    contact = Contact(
        contact_id=1,
        name="Никита",
        firstname="Малютин",
        number=79161234567,
        birthday="2006-05-15",
        user=user,
        group=group,
        is_favorite=False,
    )

    assert contact.id == 1
    assert contact.user is user
    assert contact.group is group
    assert contact.user.name == "Максим"
    assert contact.group.name == "Друзья"
    assert "Никита" in str(contact)


def test_contact_toggle_favorite() -> None:
    user = User(1, "Максим", "m@ex.com")
    group = Group(1, "Друзья", "Круг")
    contact = Contact(1, "А", "Б", 123, "2000-01-01", user, group, False)

    assert contact.is_favorite is False
    contact.toggle_favorite()
    assert contact.is_favorite is True


def test_search_and_sort_contacts() -> None:
    user = User(1, "Владелец", "v@ex.com")
    g1 = Group(1, "Работа", "Офис")
    contacts: list[Contact] = []

    c1 = add_contact(
        contacts, "Борис", "Белов", 79001, date(1990, 1, 1), user, g1
    )
    c2 = add_contact(
        contacts, "Анна", "Алиева", 79002, date(1995, 2, 2), user, g1, True
    )

    found = search_contacts(contacts, "Алиева")
    assert len(found) == 1
    assert found[0] is c2

    favs = get_favorite_contacts(contacts)
    assert len(favs) == 1
    assert favs[0] is c2

    sorted_list = sort_contacts_by_name(contacts)
    assert sorted_list[0] is c2
    assert sorted_list[1] is c1 

    assert delete_contact(contacts, c1.id) is True
    assert len(contacts) == 1