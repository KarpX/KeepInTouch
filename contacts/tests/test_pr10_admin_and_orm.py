from datetime import date
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from contacts.admin import ContactAdmin, ContactInline, GroupAdmin
from contacts.context_processors import kit_context
from contacts.models import Contact, Group


class DummyRequest:
    def __init__(self, user=None):
        self.user = user


class MockMessageUser:
    def __init__(self):
        self.messages = []

    def message_user(self, request, message, level):
        self.messages.append((message, level))


class Pr10AdminAndOrmTests(TestCase):
    """
    Автоматизированные тесты для проверки требований ПР10:
    - TextChoices и методы собственного менеджера (ContactQuerySet);
    - Вычисляемое поле GeneratedField (has_surname);
    - Автогенерация SlugField и метод get_absolute_url();
    - Контекстный процессор kit_context;
    - Настройки Django Admin (list_display, list_filter, inlines, actions, search_fields);
    - Оптимизация запросов через select_related (устранение N+1).
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()

        self.user = User.objects.create_user(
            username="owner_user",
            email="owner@example.com",
            password="testpassword123",
        )
        self.group = Group.objects.create(
            name="Коллеги",
            description="Рабочие контакты",
            owner=self.user,
        )

        self.contact1 = Contact.objects.create(
            name="Иван",
            firstname="Петров",
            number=79991112233,
            birthday=date(1990, 5, 15),
            status=Contact.Status.ACTIVE,
            is_favorite=True,
            owner=self.user,
            group=self.group,
        )
        self.contact2 = Contact.objects.create(
            name="Ольга",
            firstname="",
            number=79994445566,
            birthday=date(1995, 5, 20),
            status=Contact.Status.ARCHIVED,
            is_favorite=False,
            owner=self.user,
            group=self.group,
        )
        self.contact3 = Contact.objects.create(
            name="Сергей",
            firstname="Кузнецов",
            number=79997778899,
            birthday=date(1985, 12, 1),
            status=Contact.Status.BLOCKED,
            is_favorite=False,
            owner=self.user,
            group=None,
        )

    def test_status_text_choices_and_manager(self):
        """Проверка TextChoices (Contact.Status) и методов QuerySet/Manager."""
        self.assertEqual(Contact.Status.ACTIVE, "active")
        self.assertEqual(Contact.Status.ARCHIVED, "archived")
        self.assertEqual(Contact.Status.BLOCKED, "blocked")

        active_contacts = list(Contact.objects.active())
        self.assertIn(self.contact1, active_contacts)
        self.assertNotIn(self.contact2, active_contacts)
        self.assertNotIn(self.contact3, active_contacts)

        archived_contacts = list(Contact.objects.archived())
        self.assertIn(self.contact2, archived_contacts)
        self.assertNotIn(self.contact1, archived_contacts)

        blocked_contacts = list(Contact.objects.blocked())
        self.assertIn(self.contact3, blocked_contacts)

        favorite_contacts = list(Contact.objects.favorites())
        self.assertIn(self.contact1, favorite_contacts)
        self.assertNotIn(self.contact2, favorite_contacts)

        may_birthdays = list(Contact.objects.for_birthday_month(5))
        self.assertEqual(len(may_birthdays), 2)
        self.assertIn(self.contact1, may_birthdays)
        self.assertIn(self.contact2, may_birthdays)

    def test_generated_field_has_surname(self):
        """Проверка вычисляемого базой данных поля has_surname (GeneratedField)."""
        c1 = Contact.objects.get(pk=self.contact1.pk)
        c2 = Contact.objects.get(pk=self.contact2.pk)

        self.assertTrue(c1.has_surname)
        self.assertFalse(c2.has_surname)

        # Обновляем фамилию и проверяем автопересчет в БД
        c2.firstname = "Сидорова"
        c2.save(update_fields=["firstname"])
        c2.refresh_from_db()
        self.assertTrue(c2.has_surname)

    def test_slug_generation_and_get_absolute_url(self):
        """Проверка автогенерации латинского slug и метода get_absolute_url()."""
        c1 = Contact.objects.get(pk=self.contact1.pk)
        self.assertTrue(bool(c1.slug))
        self.assertIn("ivan", c1.slug.lower())
        self.assertIn(str(c1.pk), c1.slug)

        url = c1.get_absolute_url()
        self.assertEqual(url, reverse("contacts:contact_detail_slug", kwargs={"slug": c1.slug}))

        # Проверка открытия страницы по slug
        self.client.login(username="owner_user", password="testpassword123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, c1.name)

    def test_kit_context_processor(self):
        """Проверка работы контекстного процессора kit_context."""
        request = self.factory.get("/")
        request.user = self.user
        ctx = kit_context(request)

        self.assertEqual(ctx["site_name"], "KeepInTouch")
        self.assertGreaterEqual(ctx["global_contacts_count"], 3)
        self.assertGreaterEqual(ctx["global_groups_count"], 1)
        self.assertEqual(ctx["contacts_count"], 3)
        self.assertEqual(ctx["groups_count"], 1)

    def test_admin_classes_and_inlines(self):
        """Проверка настроек ModelAdmin для Contact и Group."""
        contact_admin = ContactAdmin(Contact, self.site)
        group_admin = GroupAdmin(Group, self.site)

        # ContactAdmin проверки
        self.assertIn("name", contact_admin.list_display)
        self.assertIn("status", contact_admin.list_display)
        self.assertIn("has_surname", contact_admin.list_display)
        self.assertIn("status", contact_admin.list_editable)
        self.assertIn("is_favorite", contact_admin.list_editable)
        self.assertIn("status", contact_admin.list_filter)
        self.assertIn("slug", contact_admin.readonly_fields)
        self.assertIn("group__name", contact_admin.search_fields)
        self.assertEqual(contact_admin.date_hierarchy, "birthday")
        self.assertTrue(contact_admin.view_on_site)

        # GroupAdmin проверки и inline
        self.assertIn(ContactInline, group_admin.inlines)
        self.assertEqual(group_admin.list_select_related, ("owner",))
        self.assertIn("contacts_count", group_admin.list_display)
        self.assertIn("active_contacts_count", group_admin.list_display)
        request = self.factory.get("/admin/contacts/group/")
        request.user = self.user
        qs = group_admin.get_queryset(request)
        annotated_group = qs.get(pk=self.group.pk)
        self.assertEqual(group_admin.contacts_count(annotated_group), 2)
        self.assertEqual(group_admin.active_contacts_count(annotated_group), 1)

    def test_group_admin_contacts_count_no_n_plus_one(self):
        """
        Проверка отсутствия проблемы N+1 запросов при отображении групп и подсчете контактов.
        Аннотация Count() + list_select_related('owner') должны выполнять ровно 1 SQL-запрос.
        """
        # Создаем еще несколько групп с контактами
        group2 = Group.objects.create(name="Семья", description="Семейные", owner=self.user)
        group3 = Group.objects.create(name="Друзья", description="Дружеские", owner=self.user)
        Contact.objects.create(
            name="Анна",
            firstname="Смирнова",
            number=79990001122,
            birthday=date(1992, 3, 10),
            status=Contact.Status.ACTIVE,
            owner=self.user,
            group=group2,
        )
        Contact.objects.create(
            name="Дмитрий",
            firstname="Попов",
            number=79990003344,
            birthday=date(1988, 7, 25),
            status=Contact.Status.ACTIVE,
            owner=self.user,
            group=group3,
        )

        group_admin = GroupAdmin(Group, self.site)
        request = self.factory.get("/admin/contacts/group/")
        request.user = self.user

        with CaptureQueriesContext(connection) as queries:
            groups_qs = list(group_admin.get_queryset(request))
            for grp in groups_qs:
                _ = grp.owner.username  # Проверяем доступ к связанному владельцу
                _ = group_admin.contacts_count(grp)  # Подсчет всех контактов
                _ = group_admin.active_contacts_count(grp)  # Подсчет активных контактов

        # Ровно 1 SQL-запрос со всеми LEFT OUTER JOIN и GROUP BY
        self.assertEqual(len(queries), 1)

    def test_admin_custom_actions(self):
        """Проверка массовых действий ModelAdmin."""
        contact_admin = ContactAdmin(Contact, self.site)
        request = self.factory.get("/admin/contacts/contact/")
        request.user = self.user

        # Добавляем метод message_user через миксин/патч
        messages_collector = []
        contact_admin.message_user = lambda req, msg, lvl: messages_collector.append(msg)

        qs = Contact.objects.filter(pk=self.contact1.pk)
        contact_admin.mark_as_archived(request, qs)
        self.contact1.refresh_from_db()
        self.assertEqual(self.contact1.status, Contact.Status.ARCHIVED)
        self.assertTrue(len(messages_collector) > 0)

        contact_admin.mark_as_active(request, qs)
        self.contact1.refresh_from_db()
        self.assertEqual(self.contact1.status, Contact.Status.ACTIVE)

    def test_select_related_prevents_n_plus_one(self):
        """Проверка устранения N+1 запросов через select_related('group', 'owner')."""
        with CaptureQueriesContext(connection) as queries:
            contacts = list(
                Contact.objects.select_related("group", "owner").filter(owner=self.user)
            )
            for c in contacts:
                _ = c.owner.username
                if c.group:
                    _ = c.group.name

        # Должен быть ровно 1 SQL-запрос благодаря JOIN
        self.assertEqual(len(queries), 1)

    def test_statistics_view_counts_statuses(self):
        """Проверка корректного подсчета статусов на странице статистики."""
        response = self.client.get(reverse("contacts:statistics"))
        self.assertEqual(response.status_code, 200)
        summary = response.context["summary"]
        self.assertEqual(summary["active_contacts"], 1)
        self.assertEqual(summary["archived_contacts"], 1)
        self.assertEqual(summary["blocked_contacts"], 1)
        self.assertEqual(summary["favorite_contacts"], 1)
