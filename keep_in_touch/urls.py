from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("contacts/", include("contacts.urls")),
    path("", lambda request: redirect("contacts:contact_list")),
]
