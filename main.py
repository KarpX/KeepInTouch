import os
from models.contacts import (
    Contact,
    add_contact,
    delete_contact,
    find_contact_by_id,
    get_favorite_contacts,
    search_contacts,
    sort_contacts_by_name,
)
from models.groups import Group, add_group, find_group_by_id
from models.users import User, add_user, find_user_by_id
from storage import load_all_data, save_all_data
from utils import input_bool, input_date, input_int

USERS_FILE = os.path.join("data", "users.json")
GROUPS_FILE = os.path.join("data", "groups.json")
CONTACTS_FILE = os.path.join("data", "contacts.json")


def show_contacts(contacts: list[Contact]) -> None:
    if not contacts:
        print("Контакты не найдены.")
        return
    sep = "=" * 36
    for c in contacts:
        print(sep)
        print(c)
    print(sep)


def create_new_contact_flow(
    contacts: list[Contact],
    users: list[User],
    groups: list[Group],
) -> None:
    if not users or not groups:
        print("Ошибка: в системе должны быть хотя бы один пользователь и группа!")
        return

    print("\n--- Добавление нового контакта ---")
    name = input("Имя: ").strip()
    firstname = input("Фамилия: ").strip()
    number = input_int("Номер телефона: ")
    birthday = input_date("Дата рождения (ГГГГ-ММ-ДД): ")

    print("\nДоступные пользователи (владельцы):")
    for u in users:
        print(f"  ID {u.id}: {u.name}")
    user_id = input_int("Выберите ID пользователя: ")
    user_obj = find_user_by_id(users, user_id)
    if user_obj is None:
        print("Пользователь с таким ID не найден. Отмена.")
        return

    print("\nДоступные группы:")
    for g in groups:
        print(f"  ID {g.id}: {g.name}")
    group_id = input_int("Выберите ID группы: ")
    group_obj = find_group_by_id(groups, group_id)
    if group_obj is None:
        print("Группа с таким ID не найдена. Отмена.")
        return

    is_fav = input_bool("Добавить в избранное? (да/нет): ")
    new_c = add_contact(
        contacts=contacts,
        name=name,
        firstname=firstname,
        number=number,
        birthday=birthday,
        user=user_obj,
        group=group_obj,
        is_favorite=is_fav,
    )
    print(f"\nУспешно создан контакт ID {new_c.id}!")


def main() -> None:
    users, groups, contacts = load_all_data(
        USERS_FILE, GROUPS_FILE, CONTACTS_FILE
    )

    while True:
        print("\n=== KeepInTouch (ООП версия) ===")
        print("1. Показать все контакты")
        print("2. Показать избранные контакты")
        print("3. Поиск контактов")
        print("4. Добавить контакт")
        print("5. Переключить статус «Избранное» у контакта")
        print("6. Удалить контакт")
        print("7. Показать пользователей системы")
        print("8. Добавить пользователя")
        print("9. Показать группы")
        print("10. Добавить группу")
        print("0. Сохранить и выйти")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            sorted_contacts = sort_contacts_by_name(contacts)
            show_contacts(sorted_contacts)
        elif choice == "2":
            show_contacts(get_favorite_contacts(contacts))
        elif choice == "3":
            q = input("Введите строку поиска: ").strip()
            show_contacts(search_contacts(contacts, q))
        elif choice == "4":
            create_new_contact_flow(contacts, users, groups)
            save_all_data(
                USERS_FILE, GROUPS_FILE, CONTACTS_FILE, users, groups, contacts
            )
        elif choice == "5":
            c_id = input_int("Введите ID контакта: ")
            c = find_contact_by_id(contacts, c_id)
            if c:
                c.toggle_favorite()
                save_all_data(
                    USERS_FILE, GROUPS_FILE, CONTACTS_FILE, users, groups, contacts
                )
                print(f"Статус избранного изменен на: {c.is_favorite}")
            else:
                print("Контакт не найден.")
        elif choice == "6":
            c_id = input_int("Введите ID контакта: ")
            if delete_contact(contacts, c_id):
                save_all_data(
                    USERS_FILE, GROUPS_FILE, CONTACTS_FILE, users, groups, contacts
                )
                print("Контакт удален.")
            else:
                print("Контакт не найден.")
        elif choice == "7":
            for u in users:
                print(u)
        elif choice == "8":
            uname = input("Имя пользователя: ").strip()
            uemail = input("Email: ").strip()
            add_user(users, uname, uemail)
            save_all_data(
                USERS_FILE, GROUPS_FILE, CONTACTS_FILE, users, groups, contacts
            )
            print("Пользователь добавлен.")
        elif choice == "9":
            for g in groups:
                print(g)
        elif choice == "10":
            gname = input("Название группы: ").strip()
            gdesc = input("Описание: ").strip()
            add_group(groups, gname, gdesc)
            save_all_data(
                USERS_FILE, GROUPS_FILE, CONTACTS_FILE, users, groups, contacts
            )
            print("Группа создана.")
        elif choice == "0":
            save_all_data(
                USERS_FILE, GROUPS_FILE, CONTACTS_FILE, users, groups, contacts
            )
            print("Данные сохранены. Работа завершена.")
            break
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()