from models.groups import Group, add_group, find_group_by_id


def test_group_creation() -> None:
    group = Group(group_id=1, name="Работа", description="Коллеги по цеху")
    assert group.id == 1
    assert group.name == "Работа"
    assert "Работа" in str(group)


def test_add_and_find_group() -> None:
    groups: list[Group] = []
    g = add_group(groups, "Семья", "Родственники")
    assert len(groups) == 1
    assert find_group_by_id(groups, g.id) is g
    assert find_group_by_id(groups, 404) is None