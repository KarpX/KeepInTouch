from django.contrib import admin
from .models import Contact, Group


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "firstname",
        "number",
        "group",
        "owner",
        "is_favorite",
    )
    list_filter = ("is_favorite", "group", "owner")
    search_fields = ("name", "firstname", "number", "tags")
    list_editable = ("is_favorite",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "description")
    search_fields = ("name", "description")
    list_filter = ("owner",)
