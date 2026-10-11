from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed
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
        context = {
            "total_contacts": total_contacts,
            "favorite_contacts": favorite_contacts,
            "total_groups": total_groups,
            "recent_contacts": recent_contacts,
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

    groups = Group.objects.filter(owner=request.user)
    return render(
        request,
        "contacts/contact_list.html",
        {
            "contacts": contacts,
            "query": query,
            "groups": groups,
            "selected_group": int(group_id) if group_id.isdigit() else None,
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
    return render(
        request,
        "contacts/contact_list.html",
        {
            "contacts": contacts,
            "query": query,
            "is_favorites_view": True,
        },
    )


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)
    return render(request, "contacts/contact_detail.html", {"contact": contact})


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
        .order_by("name")
    )
    return render(request, "contacts/group_list.html", {"groups": groups})


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
