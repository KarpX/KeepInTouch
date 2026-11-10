from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Min, Q, Value
from django.db.models.functions import Coalesce
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
    """
    ПР10: Каталог контактов с фильтрацией, динамической сортировкой и пагинацией (Paginator).
    Использует собственный менеджер Contact.objects.active().
    """
    contacts = Contact.objects.active().filter(owner=request.user).select_related("group", "owner")
    query = request.GET.get("q", "").strip()
    group_id = request.GET.get("group", "").strip()
    sort = request.GET.get("sort", "name").strip()

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

    # Безопасная сортировка по белому списку полей (подраздел 5.14)
    sort_fields = {
        "name": "name",
        "firstname": "firstname",
        "date": "birthday",
        "number": "number",
        "group": "group__name",
    }
    sort_field = sort_fields.get(sort, "name")
    contacts = contacts.order_by(sort_field, "id")

    groups = Group.objects.filter(owner=request.user).annotate(contacts_count=Count("contacts"))
    total_contacts_count = Contact.objects.filter(owner=request.user).count()
    favorites_count = Contact.objects.filter(owner=request.user, is_favorite=True).count()

    paginator = Paginator(contacts, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "contacts/contact_list.html",
        {
            "contacts": page_obj,
            "page_obj": page_obj,
            "query": query,
            "groups": groups,
            "selected_group": int(group_id) if group_id.isdigit() else None,
            "sort": sort,
            "total_contacts_count": total_contacts_count,
            "favorites_count": favorites_count,
            "is_favorites_view": False,
        },
    )


@login_required
def contact_favorites(request):
    """
    ПР9: Избранные контакты с фильтрацией, сортировкой и пагинацией.
    """
    contacts = Contact.objects.filter(
        owner=request.user, is_favorite=True
    ).select_related("group", "owner")
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name").strip()

    if query:
        contacts = contacts.filter(
            Q(name__icontains=query)
            | Q(firstname__icontains=query)
            | Q(number__icontains=query)
            | Q(tags__icontains=query)
            | Q(group__name__icontains=query)
        )

    sort_fields = {
        "name": "name",
        "firstname": "firstname",
        "date": "birthday",
        "number": "number",
        "group": "group__name",
    }
    sort_field = sort_fields.get(sort, "name")
    contacts = contacts.order_by(sort_field, "id")

    groups = Group.objects.filter(owner=request.user).annotate(contacts_count=Count("contacts"))
    total_contacts_count = Contact.objects.filter(owner=request.user).count()
    favorites_count = Contact.objects.filter(owner=request.user, is_favorite=True).count()

    paginator = Paginator(contacts, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "contacts/contact_list.html",
        {
            "contacts": page_obj,
            "page_obj": page_obj,
            "query": query,
            "groups": groups,
            "sort": sort,
            "total_contacts_count": total_contacts_count,
            "favorites_count": favorites_count,
            "is_favorites_view": True,
        },
    )


@login_required
def contact_detail(request, pk=None, slug=None):
    """
    ПР10: Карточка контакта с получением через get_object_or_404 (по slug или pk)
    и жадной загрузкой (select_related).
    """
    lookup = {"owner": request.user}
    if slug:
        lookup["slug"] = slug
    else:
        lookup["pk"] = pk
    contact = get_object_or_404(
        Contact.objects.select_related("group", "owner"),
        **lookup,
    )
    context = {"contact": contact}
    return render(request, "contacts/contact_detail.html", context)


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
# ПР9: Представления аналитики, поиска и каталога на Django ORM
# ==============================================================================

def contact_statistics(request):
    """
    ПР9: Аналитика и статистика базы данных на чистом Django ORM.
    Демонстрирует:
    - Агрегирование (aggregate) с функциями Count, Min, Max;
    - Условную фильтрацию внутри агрегата (filter=Q(is_favorite=True));
    - Группировку и аннотирование (annotate) с подсчетом связанных объектов Count("contacts");
    - Фильтрацию по агрегированному полю (аналог SQL HAVING: contacts_count__gt=1);
    - Поиск пустых групп без связанных контактов (аналог SQL NOT IN: contacts__isnull=True).
    """
    # 1. Агрегаты: общее число контактов, распределение по статусам и число избранных (ПР10)
    summary = Contact.objects.aggregate(
        total_contacts=Count("id"),
        active_contacts=Count("id", filter=Q(status=Contact.Status.ACTIVE)),
        archived_contacts=Count("id", filter=Q(status=Contact.Status.ARCHIVED)),
        blocked_contacts=Count("id", filter=Q(status=Contact.Status.BLOCKED)),
        favorite_contacts=Count("id", filter=Q(is_favorite=True)),
    )

    # 2. Экстремумы дат рождения (MIN, MAX)
    birthdays_extremes = Contact.objects.aggregate(
        oldest_birthday=Min("birthday"),
        youngest_birthday=Max("birthday"),
    )

    # 3. Распределение контактов по группам (LEFT JOIN + GROUP BY)
    group_stats = (
        Group.objects.annotate(
            contacts_count=Count("contacts"),
            group_name=F("name"),
            group_description=F("description"),
        )
        .values("id", "group_name", "group_description", "contacts_count")
        .order_by("-contacts_count", "group_name")
    )

    # 4. Популярные группы с числом контактов > 1 (HAVING COUNT(c.id) > 1)
    popular_groups = (
        Group.objects.annotate(
            contacts_count=Count("contacts"),
            group_name=F("name"),
        )
        .filter(contacts_count__gt=1)
        .values("id", "group_name", "contacts_count")
        .order_by("-contacts_count")
    )

    # 5. Пустые группы (подзапрос NOT IN / contacts__isnull=True)
    empty_groups = (
        Group.objects.filter(contacts__isnull=True)
        .values("id", "name", "description")
        .order_by("name")
    )

    context = {
        "summary": summary,
        "group_stats": group_stats,
        "popular_groups": popular_groups,
        "empty_groups": empty_groups,
        "birthdays_extremes": birthdays_extremes,
    }
    return render(request, "contacts/statistics.html", context)


# Алиас для обратной совместимости с маршрутами и тестами ПР7
contact_statistics_sql = contact_statistics


def contact_search_date(request):
    """
    ПР9: Параметризованный поиск контактов по дате рождения через Django ORM.
    - Обрабатывает GET-параметр date с валидацией формата даты (YYYY-MM-DD);
    - При некорректной дате формирует понятную ошибку пользователю;
    - Выполняет фильтрацию (birthday__lte=selected_date) и жадную загрузку (select_related);
    - Передает данные в шаблон contacts/sql_search_date.html.
    """
    search_date = request.GET.get("date", "").strip()
    contacts = []
    error = None

    if search_date:
        try:
            selected_date = datetime.strptime(search_date, "%Y-%m-%d").date()
            contacts = (
                Contact.objects.filter(birthday__lte=selected_date)
                .select_related("group", "owner")
                .annotate(
                    group_name=Coalesce(F("group__name"), Value("Без группы")),
                    owner_name=F("owner__username"),
                )
                .order_by("-birthday")
            )
        except ValueError:
            error = "Укажите корректную дату в формате ГГГГ-ММ-ДД."

    return render(
        request,
        "contacts/sql_search_date.html",
        {
            "contacts": contacts,
            "search_date": search_date,
            "error": error,
        },
    )


# Алиас для обратной совместимости с маршрутами и тестами ПР7
contact_search_date_sql = contact_search_date


def contact_sql_list(request):
    """
    ПР9: Просмотр каталога контактов через Django ORM (select_related).
    Заменяет чистый SQL-JOIN, передавая в шаблон данные из трех связанных моделей.
    """
    contacts = (
        Contact.objects.select_related("group", "owner")
        .annotate(
            contact_id=F("id"),
            contact_name=F("name"),
            contact_firstname=F("firstname"),
            phone_number=F("number"),
            group_name=Coalesce(F("group__name"), Value("Без группы")),
            owner_username=F("owner__username"),
            owner_email=F("owner__email"),
        )
        .order_by("name", "firstname")
    )
    return render(
        request,
        "contacts/sql_contact_list.html",
        {"contacts": contacts},
    )


contact_orm_list = contact_sql_list

