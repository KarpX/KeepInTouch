from typing import Optional


class Group:

    def __init__(self, group_id: int, name: str, description: str) -> None:
        self.id = group_id
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return f"Группа [{self.id}]: {self.name} — {self.description}"

    @classmethod
    def from_data(cls, data: dict) -> "Group":
        return cls(
            group_id=data["id"],
            name=data["name"],
            description=data["description"]
        )


def add_group(groups: list[Group], name: str, description: str) -> Group:
    new_id = max([g.id for g in groups], default=0) + 1
    group = Group(group_id=new_id, name=name, description=description)
    groups.append(group)
    return group


def find_group_by_id(groups: list[Group], group_id: int) -> Optional[Group]:
    for group in groups:
        if group.id == group_id:
            return group
    return None