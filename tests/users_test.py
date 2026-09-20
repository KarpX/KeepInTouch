from models.users import User, add_user, find_user_by_id


def test_user_creation() -> None:
    user = User(user_id=1, name="Тест", email="test@example.com")
    assert user.id == 1
    assert user.name == "Тест"
    assert user.email == "test@example.com"
    assert "Тест" in str(user)


def test_user_from_data() -> None:
    data = {"id": 10, "name": "Анна", "email": "anna@test.ru"}
    user = User.from_data(data)
    assert user.id == 10
    assert user.name == "Анна"


def test_add_and_find_user() -> None:
    users: list[User] = []
    u = add_user(users, "Иван", "ivan@m.ru")
    assert len(users) == 1
    assert find_user_by_id(users, u.id) is u
    assert find_user_by_id(users, 999) is None