from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ContactForm, GroupForm
from .models import Contact, Group


def get_user_tags(user) -> list[str]:
    """Возвращает отсортированный список уникальных тегов текущего пользователя."""
    if not user.is_authenticated:
        return []
    tags_set = set()
    raw_tags_list = Contact.objects.filter(owner=user).exclude(tags="").values_list("tags", flat=True)
    for raw_tags in raw_tags_list:
        for t in raw_tags.split(","):
            cleaned = t.strip()
            if cleaned:
                tags_set.add(cleaned)
    return sorted(tags_set)


def home_view(request):
    """Главная страница приложения KeepInTouch."""
    if request.user.is_authenticated:
        total_contacts = Contact.objects.filter(owner=request.user).count()
        favorite_contacts = Contact.objects.filter(owner=request.user, is_favorite=True).count()
        total_groups = Group.objects.filter(owner=request.user).count()
        recent_contacts = (
            Contact.objects.filter(owner=request.user)
            .select_related("group")
            .order_by("-id")[:5]
        )
        all_user_contacts = list(Contact.objects.filter(owner=request.user).select_related("group"))
        upcoming_birthdays = sorted(
            [c for c in all_user_contacts if c.birthday],
            key=lambda c: (c.days_until_birthday if c.days_until_birthday is not None else 999),
        )[:3]
        context = {
            "total_contacts": total_contacts,
            "favorite_contacts": favorite_contacts,
            "total_groups": total_groups,
            "recent_contacts": recent_contacts,
            "upcoming_birthdays": upcoming_birthdays,
        }
    else:
        context = {}
    return render(request, "home.html", context)


@login_required
def contact_list(request):
    contacts = Contact.objects.filter(owner=request.user).select_related("group")
    query = request.GET.get("q", "").strip()
    group_id = request.GET.get("group", "").strip()

    if query:
        contacts = contacts.filter(
            Q(name__icontains=query)
            | Q(firstname__icontains=query)
            | Q(number__icontains=query)
            | Q(tags__icontains=query)
            | Q(group__name__icontains=query)
        )

    if group_id and group_id.isdigit():
        contacts = contacts.filter(group_id=int(group_id))

    groups = Group.objects.filter(owner=request.user).annotate(contacts_count=Count("contacts"))
    total_contacts_count = Contact.objects.filter(owner=request.user).count()
    favorites_count = Contact.objects.filter(owner=request.user, is_favorite=True).count()

    return render(
        request,
        "contacts/contact_list.html",
        {
            "contacts": contacts,
            "query": query,
            "groups": groups,
            "selected_group": int(group_id) if group_id.isdigit() else None,
            "total_contacts_count": total_contacts_count,
            "favorites_count": favorites_count,
            "is_favorites_view": False,
        },
    )


@login_required
def contact_favorites(request):
    contacts = Contact.objects.filter(
        owner=request.user, is_favorite=True
    ).select_related("group")
    query = request.GET.get("q", "").strip()
    if query:
        contacts = contacts.filter(
            Q(name__icontains=query)
            | Q(firstname__icontains=query)
            | Q(number__icontains=query)
            | Q(tags__icontains=query)
            | Q(group__name__icontains=query)
        )
    groups = Group.objects.filter(owner=request.user).annotate(contacts_count=Count("contacts"))
    total_contacts_count = Contact.objects.filter(owner=request.user).count()
    favorites_count = Contact.objects.filter(owner=request.user, is_favorite=True).count()
    return render(
        request,
        "contacts/contact_list.html",
        {
            "contacts": contacts,
            "query": query,
            "groups": groups,
            "total_contacts_count": total_contacts_count,
            "favorites_count": favorites_count,
            "is_favorites_view": True,
        },
    )


@login_required
def contact_detail(request, pk):
    contact = Contact.objects.filter(pk=pk, owner=request.user).select_related("group").first()
    context = {"contact": contact}
    return render(
        request,
        "contacts/contact_detail.html",
        context,
        status=404 if contact is None else 200,
    )


@login_required
def contact_create(request):
    existing_tags = get_user_tags(request.user)
    if request.method == "POST":
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            return redirect("contacts:contact_detail", pk=contact.pk)
    else:
        initial_group = request.GET.get("group")
        initial = {"group": initial_group} if initial_group else {}
        form = ContactForm(user=request.user, initial=initial)

    return render(
        request,
        "contacts/contact_form.html",
        {
            "form": form,
            "title": "Новый контакт",
            "button_text": "Создать контакт",
            "existing_tags": existing_tags,
        },
    )


@login_required
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)
    existing_tags = get_user_tags(request.user)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("contacts:contact_detail", pk=contact.pk)
    else:
        form = ContactForm(instance=contact, user=request.user)

    return render(
        request,
        "contacts/contact_form.html",
        {
            "form": form,
            "contact": contact,
            "title": f"Редактирование: {contact}",
            "button_text": "Сохранить изменения",
            "existing_tags": existing_tags,
        },
    )


@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)
    if request.method == "POST":
        contact.delete()
        return redirect("contacts:contact_list")
    return render(
        request, "contacts/contact_confirm_delete.html", {"contact": contact}
    )


@login_required
def contact_toggle_favorite(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)
    if request.method == "POST":
        contact.toggle_favorite()
        next_url = request.POST.get("next") or request.META.get(
            "HTTP_REFERER"
        ) or "contacts:contact_list"
        return redirect(next_url)
    return HttpResponseNotAllowed(["POST"])


@login_required
def group_list(request):
    groups = (
        Group.objects.filter(owner=request.user)
        .annotate(contacts_count=Count("contacts"))
        .prefetch_related("contacts")
        .order_by("name")
    )
    tag_counts = {}
    for raw_tags in Contact.objects.filter(owner=request.user).exclude(tags="").values_list("tags", flat=True):
        for t in raw_tags.split(","):
            cleaned = t.strip()
            if cleaned:
                tag_counts[cleaned] = tag_counts.get(cleaned, 0) + 1
    sorted_tag_counts = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))[:12]

    return render(
        request,
        "contacts/group_list.html",
        {
            "groups": groups,
            "tag_counts": sorted_tag_counts,
        },
    )


@login_required
def group_create(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            return redirect("contacts:group_list")
    else:
        form = GroupForm()

    return render(
        request,
        "contacts/group_form.html",
        {"form": form, "title": "Новая группа", "button_text": "Создать группу"},
    )


@login_required
def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk, owner=request.user)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("contacts:group_list")
    else:
        form = GroupForm(instance=group)

    return render(
        request,
        "contacts/group_form.html",
        {
            "form": form,
            "group": group,
            "title": f"Редактирование группы: {group.name}",
            "button_text": "Сохранить изменения",
        },
    )


@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk, owner=request.user)
    if request.method == "POST":
        group.delete()
        return redirect("contacts:group_list")
    return render(
        request, "contacts/group_confirm_delete.html", {"group": group}
    )


# ==============================================================================
# ПР7: Представления прямого SQL (без Django ORM)
# ==============================================================================

def contact_statistics_sql(request):
    """
    ПР7: Страница статистики базы данных.
    Формируется на стороне СУБД с помощью чистого SQL без Django ORM:
    - LEFT JOIN и GROUP BY для распределения контактов по группам;
    - HAVING для фильтрации групп с числом контактов > 1;
    - Агрегатные функции COUNT(*) и SUM/FILTER для общих показателей;
    - Вложенный подзапрос NOT IN для выявления пустых групп.
    """
    from db.database import get_connection

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Агрегаты: общее число контактов и избранных
            cur.execute("""
                SELECT 
                    COUNT(*) AS total_contacts,
                    COUNT(CASE WHEN is_favorite THEN 1 END) AS favorite_contacts
                FROM contacts_contact;
            """)
            summary = cur.fetchone() or {"total_contacts": 0, "favorite_contacts": 0}

            # 2. Распределение по группам (LEFT JOIN + GROUP BY)
            cur.execute("""
                SELECT 
                    g.id AS group_id,
                    g.name AS group_name,
                    g.description AS group_description,
                    COUNT(c.id) AS contacts_count
                FROM contacts_group AS g
                LEFT JOIN contacts_contact AS c ON g.id = c.group_id
                GROUP BY g.id, g.name, g.description
                ORDER BY contacts_count DESC, g.name ASC;
            """)
            group_stats = cur.fetchall()

            # 3. Популярные группы с HAVING count > 1
            cur.execute("""
                SELECT 
                    g.id AS group_id,
                    g.name AS group_name,
                    COUNT(c.id) AS contacts_count
                FROM contacts_group AS g
                JOIN contacts_contact AS c ON g.id = c.group_id
                GROUP BY g.id, g.name
                HAVING COUNT(c.id) > 1
                ORDER BY contacts_count DESC;
            """)
            popular_groups = cur.fetchall()

            # 4. Пустые группы (подзапрос NOT IN)
            cur.execute("""
                SELECT 
                    g.id,
                    g.name,
                    g.description
                FROM contacts_group AS g
                WHERE g.id NOT IN (
                    SELECT DISTINCT c.group_id 
                    FROM contacts_contact AS c 
                    WHERE c.group_id IS NOT NULL
                )
                ORDER BY g.name;
            """)
            empty_groups = cur.fetchall()

            # 5. Экстремумы дат рождения (MIN, MAX)
            cur.execute("""
                SELECT 
                    MIN(birthday) AS oldest_birthday,
                    MAX(birthday) AS youngest_birthday
                FROM contacts_contact;
            """)
            birthdays_extremes = cur.fetchone() or {}
    finally:
        conn.close()

    context = {
        "summary": summary,
        "group_stats": group_stats,
        "popular_groups": popular_groups,
        "empty_groups": empty_groups,
        "birthdays_extremes": birthdays_extremes,
    }
    return render(request, "contacts/statistics.html", context)


def contact_search_date_sql(request):
    """
    ПР7: Параметризованный поиск контактов по дате рождения.
    Использует параметризованный запрос с заполнителями %s для защиты от SQL-инъекций.
    """
    from db.database import get_connection

    search_date = request.GET.get("date", "").strip()
    contacts = []
    if search_date:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.id,
                        c.name,
                        c.firstname,
                        c.number,
                        c.birthday,
                        c.is_favorite,
                        COALESCE(g.name, 'Без группы') AS group_name,
                        u.username AS owner_name
                    FROM contacts_contact AS c
                    LEFT JOIN contacts_group AS g ON c.group_id = g.id
                    JOIN auth_user AS u ON c.owner_id = u.id
                    WHERE c.birthday <= %s
                    ORDER BY c.birthday DESC;
                """, [search_date])
                contacts = cur.fetchall()
        finally:
            conn.close()

    return render(
        request,
        "contacts/sql_search_date.html",
        {"contacts": contacts, "search_date": search_date},
    )


def contact_sql_list(request):
    """
    ПР7: Просмотр списка контактов с объединением трех таблиц через чистый SQL (JOIN).
    Демонстрирует named access через dict_row и работу без Django ORM.
    """
    from db.database import get_connection

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    c.id AS contact_id,
                    c.name AS contact_name,
                    c.firstname AS contact_firstname,
                    c.number AS phone_number,
                    c.birthday,
                    c.is_favorite,
                    COALESCE(g.name, 'Без группы') AS group_name,
                    u.username AS owner_username,
                    u.email AS owner_email
                FROM contacts_contact AS c
                LEFT JOIN contacts_group AS g ON c.group_id = g.id
                JOIN auth_user AS u ON c.owner_id = u.id
                ORDER BY c.name ASC, c.firstname ASC;
            """)
            contacts = cur.fetchall()
    finally:
        conn.close()

    return render(
        request,
        "contacts/sql_contact_list.html",
        {"contacts": contacts},
    )

