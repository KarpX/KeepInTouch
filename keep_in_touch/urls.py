from django.contrib import admin
from django.urls import include, path
from contacts.views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("contacts/", include("contacts.urls")),
    path("", home_view, name="home"),
]
