from datetime import date

name = "Максим"
firstname = "Карпеев"
number = 79153791828
birthday = date(2006, 3, 10)
is_favorite = False

contacts = [{
    "name": name,
    "firstname": firstname,
    "number": number,
    "birthday": birthday,
    "is_favorite": is_favorite
}]

def get_contact_info(contact):
    return (f"Имя: {contact['name']}\n"
            f"Фамилия: {contact['firstname']}\n"
            f"Номер: {contact['number']}\n"
            f"Дата рождения: {contact['birthday']}\n"
            f"Избранный: {'Да' if contact['is_favorite'] else 'Нет'}")

def add_contact(name, firstname, number, birthday, is_favorite):
    contact = {
        "name": name,
        "firstname": firstname,
        "number": number,
        "birthday": birthday,
        "is_favorite": is_favorite
    }
    contacts.append(contact)

def delete_contact(index):
    if 0 <= index < len(contacts):
        del contacts[index]
    else:
        print("Контакт с таким индексом не существует.")

def edit_contact(index, name=None, firstname=None, number=None, birthday=None, is_favorite=None):
    if 0 <= index < len(contacts):
        contact = contacts[index]
        if name is not None:
            contact['name'] = name
        if firstname is not None:
            contact['firstname'] = firstname
        if number is not None:
            contact['number'] = number
        if birthday is not None:
            contact['birthday'] = birthday
        if is_favorite is not None:
            contact['is_favorite'] = is_favorite
    else:
        print("Контакт с таким индексом не существует.")

def get_favorite_contacts():
    return [contact for contact in contacts if contact['is_favorite']]

def search_contacts(query):
    return [contact for contact in contacts if query.lower() in contact['name'].lower() or query.lower() in contact['firstname'].lower()
            or query.lower() in str(contact['number']).lower()]

add_contact("Никита", "Малютин", 79165556767, date(2006, 5, 15), True)
print(get_contact_info(contacts[0]))
print("--------------------------------")
print(get_contact_info(contacts[1]))
print("--------------------------------")
print(f"\nИзбранные контакты: {get_favorite_contacts()}")
print("--------------------------------")
print("\nИзменение контакта:")
edit_contact(0, name="Максим", firstname="Карпеев 2.0 (переименован)", number=79153791828, birthday=date(2006, 3, 10), is_favorite=False)
print(get_contact_info(contacts[0]))
print("--------------------------------")
print(f"\nКоличество контактов: {len(contacts)}")
delete_contact(1)
print(f"\nКоличество контактов после удаления: {len(contacts)}")

print("--------------------------------")
print(f"\nПоиск контактов по имени 'Максим':")
for contact in search_contacts("Максим"):
    print(get_contact_info(contact))

print("--------------------------------")
print(f"\nПоиск контактов по имени номеру 79153791828:")
for contact in search_contacts("79153791828"):
    print(get_contact_info(contact))