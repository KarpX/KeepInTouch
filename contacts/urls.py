from django.urls import path
from . import views

app_name = "contacts"

urlpatterns = [
    path("", views.contact_list, name="contact_list"),
    path("favorites/", views.contact_favorites, name="favorites"),
    path("add/", views.contact_create, name="contact_create"),
    path("<int:pk>/", views.contact_detail, name="contact_detail"),
    path("<int:pk>/edit/", views.contact_update, name="contact_update"),
    path("<int:pk>/delete/", views.contact_delete, name="contact_delete"),
    path("<int:pk>/toggle-favorite/", views.contact_toggle_favorite, name="toggle_favorite"),
    path("groups/", views.group_list, name="group_list"),
    path("groups/add/", views.group_create, name="group_create"),
    path("groups/<int:pk>/edit/", views.group_update, name="group_update"),
    path("groups/<int:pk>/delete/", views.group_delete, name="group_delete"),
    # ПР7: Маршруты для прямого SQL-слоя
    path("statistics/", views.contact_statistics_sql, name="statistics"),
    path("by-date/", views.contact_search_date_sql, name="search_date"),
    path("available/", views.contact_search_date_sql, name="available"),
    path("sql-list/", views.contact_sql_list, name="sql_list"),
]
