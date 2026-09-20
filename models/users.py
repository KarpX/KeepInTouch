from typing import Optional


class User:

    def __init__(self, user_id: int, name: str, email: str) -> None:
        self.id = user_id
        self.name = name
        self.email = email

    def __str__(self) -> str:
        return f"Пользователь [{self.id}]: {self.name} ({self.email})"

    @classmethod
    def from_data(cls, data: dict) -> "User":
        return cls(
            user_id=data["id"],
            name=data["name"],
            email=data["email"]
        )

    @staticmethod
    def validate_email(email: str) -> bool:
        return "@" in email and "." in email


def add_user(users: list[User], name: str, email: str) -> User:
    new_id = max([u.id for u in users], default=0) + 1
    user = User(user_id=new_id, name=name, email=email)
    users.append(user)
    return user


def find_user_by_id(users: list[User], user_id: int) -> Optional[User]:
    for user in users:
        if user.id == user_id:
            return user
    return None