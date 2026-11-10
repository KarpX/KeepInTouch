from .models import Contact, Group


def kit_context(request):
    """
    Пользовательский контекстный процессор KeepInTouch (ПР10).
    Предоставляет глобальное имя сервиса и актуальные счетчики
    контактов и групп для использования в базовых шаблонах.
    """
    total_contacts_count = Contact.objects.count()
    total_groups_count = Group.objects.count()

    user_contacts_count = 0
    user_groups_count = 0
    if request.user.is_authenticated:
        user_contacts_count = Contact.objects.filter(owner=request.user).count()
        user_groups_count = Group.objects.filter(owner=request.user).count()

    return {
        "site_name": "KeepInTouch",
        "site_subtitle": "Система управления персональными контактами и связями",
        "global_contacts_count": total_contacts_count,
        "global_groups_count": total_groups_count,
        "contacts_count": user_contacts_count if request.user.is_authenticated else total_contacts_count,
        "groups_count": user_groups_count if request.user.is_authenticated else total_groups_count,
    }
