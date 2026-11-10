from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html

from .models import Contact, Group


class ContactInline(admin.TabularInline):
    """
    Встроенная таблица связанных контактов в карточке группы (ПР10, п. 5.2.5.4).
    """
    model = Contact
    fields = ("name", "firstname", "number", "status", "is_favorite")
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Административный интерфейс модели Group (ПР10).
    """
    list_display = ("id", "name", "owner", "contacts_count", "description")
    search_fields = ("name", "description", "owner__username")
    list_filter = ("owner",)
    ordering = ("name",)
    list_per_page = 20
    inlines = (ContactInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(contacts_count_annotated=Count("contacts"))

    @admin.display(description="Контактов в группе", ordering="contacts_count_annotated")
    def contacts_count(self, obj):
        return getattr(obj, "contacts_count_annotated", obj.contacts.count())


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Административный интерфейс модели Contact (ПР10, пп. 5.2.2-5.2.5.7).
    """
    list_display = (
        "id",
        "name",
        "firstname",
        "status",
        "group",
        "owner",
        "has_surname",
        "is_favorite",
        "birthday",
        "site_link",
    )
    list_display_links = ("name",)
    list_editable = ("is_favorite", "status")
    search_fields = (
        "name",
        "firstname",
        "number",
        "tags",
        "group__name",
        "owner__username",
    )
    list_filter = (
        "status",
        "is_favorite",
        "has_surname",
        "group",
        "owner",
        "birthday",
    )
    ordering = ("name", "firstname")
    list_per_page = 20
    readonly_fields = ("id", "slug", "has_surname")
    autocomplete_fields = ("group", "owner")
    date_hierarchy = "birthday"
    view_on_site = True
    list_select_related = ("group", "owner")
    actions = ("mark_as_archived", "mark_as_active", "mark_as_favorite")

    @admin.display(description="На сайте")
    def site_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank">Открыть</a>', url)

    @admin.action(description="Архивировать выбранные контакты")
    def mark_as_archived(self, request, queryset):
        updated = queryset.update(status=Contact.Status.ARCHIVED)
        self.message_user(
            request,
            f"Архивировано контактов: {updated}.",
            messages.SUCCESS,
        )

    @admin.action(description="Вернуть выбранные контакты в активные")
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status=Contact.Status.ACTIVE)
        self.message_user(
            request,
            f"Возвращено в активные контактов: {updated}.",
            messages.SUCCESS,
        )

    @admin.action(description="Добавить выбранные контакты в избранное")
    def mark_as_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=True)
        self.message_user(
            request,
            f"Добавлено в избранное контактов: {updated}.",
            messages.SUCCESS,
        )
