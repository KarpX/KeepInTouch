from datetime import date
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Min, Q
from django.test import TestCase
from django.urls import reverse

from contacts.models import Contact, Group


class OrmLayerTests(TestCase):
    """
    ПР9: Тестирование слоя Django ORM, связей моделей, 16 ORM-выражений,
    фильтрации, сортировки, пагинации и агрегации данных.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="secretpassword",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="secretpassword",
        )

        self.group_friends = Group.objects.create(
            name="Друзья",
            description="Близкие друзья",
            owner=self.user,
        )
        self.group_work = Group.objects.create(
            name="Работа",
            description="Коллеги и партнеры",
            owner=self.user,
        )
        self.group_empty = Group.objects.create(
            name="Пустая группа",
            description="Группа без контактов",
            owner=self.user,
        )

        # Контакты пользователя self.user
        self.c1 = Contact.objects.create(
            name="Алексей",
            firstname="Смирнов",
            number=79161112233,
            birthday=date(1995, 3, 10),
            is_favorite=True,
            tags="важное, коллега",
            owner=self.user,
            group=self.group_work,
        )
        self.c2 = Contact.objects.create(
            name="Борис",
            firstname="Петров",
            number=79162223344,
            birthday=date(2000, 7, 20),
            is_favorite=False,
            tags="спорт",
            owner=self.user,
            group=self.group_friends,
        )
        self.c3 = Contact.objects.create(
            name="Владимир",
            firstname="Иванов",
            number=79163334455,
            birthday=date(1990, 1, 15),
            is_favorite=True,
            tags="важное",
            owner=self.user,
            group=self.group_work,
        )
        self.c4 = Contact.objects.create(
            name="Дмитрий",
            firstname="Сидоров",
            number=79164445566,
            birthday=date(2005, 11, 5),
            is_favorite=False,
            tags="",
            owner=self.user,
            group=None,  # контакт без группы
        )

    # --------------------------------------------------------------------------
    # 1. Базовое получение данных (all, get)
    # --------------------------------------------------------------------------
    def test_base_retrieval_all_and_get(self):
        """Проверка Contact.objects.all() и get()."""
        all_contacts = Contact.objects.all()
        self.assertEqual(all_contacts.count(), 4)

        contact = Contact.objects.get(pk=self.c1.pk)
        self.assertEqual(contact.name, "Алексей")

    # --------------------------------------------------------------------------
    # 2. Фильтрация и исключение (filter, exclude)
    # --------------------------------------------------------------------------
    def test_filtering_single_and_multiple_conditions(self):
        """Проверка фильтрации по одиночному и нескольким условиям."""
        favs = Contact.objects.filter(is_favorite=True)
        self.assertEqual(favs.count(), 2)

        work_favs = Contact.objects.filter(
            group=self.group_work, is_favorite=True
        )
        self.assertEqual(work_favs.count(), 2)

    def test_filter_by_related_model_field(self):
        """Проверка фильтрации по полю связанной модели (group__name)."""
        work_contacts = Contact.objects.filter(group__name="Работа")
        self.assertEqual(work_contacts.count(), 2)

    def test_exclude_records(self):
        """Проверка исключения записей с помощью exclude()."""
        contacts_with_tags = Contact.objects.exclude(tags="")
        self.assertEqual(contacts_with_tags.count(), 3)
        self.assertNotIn(self.c4, contacts_with_tags)

    # --------------------------------------------------------------------------
    # 3. Поиск (icontains, Q-объекты)
    # --------------------------------------------------------------------------
    def test_string_search_and_multi_field_q(self):
        """Проверка строкового поиска icontains и составного Q(...) | Q(...)."""
        by_name = Contact.objects.filter(name__icontains="лекс")
        self.assertEqual(by_name.count(), 1)
        self.assertEqual(by_name.first(), self.c1)

        by_multi = Contact.objects.filter(
            Q(name__icontains="петров")
            | Q(firstname__icontains="петров")
            | Q(number__icontains="2223344")
        )
        self.assertEqual(by_multi.count(), 1)
        self.assertEqual(by_multi.first(), self.c2)

    # --------------------------------------------------------------------------
    # 4. Сортировка (статическая и динамическая)
    # --------------------------------------------------------------------------
    def test_sorting_and_dynamic_sort(self):
        """Проверка сортировки order_by и словаря разрешенных полей."""
        # Статическая
        sorted_contacts = list(
            Contact.objects.order_by("-birthday").values_list("id", flat=True)
        )
        self.assertEqual(sorted_contacts[0], self.c4.id)  # 2005 год — самый младший

        # Динамическая
        sort_fields = {
            "name": "name",
            "date": "birthday",
            "group": "group__name",
        }
        sort_param = "name"
        field = sort_fields.get(sort_param, "name")
        names = list(
            Contact.objects.order_by(field).values_list("name", flat=True)
        )
        self.assertEqual(names, ["Алексей", "Борис", "Владимир", "Дмитрий"])

    # --------------------------------------------------------------------------
    # 5. Работа со связями (select_related, related_name)
    # --------------------------------------------------------------------------
    def test_relationships_direct_and_reverse(self):
        """Проверка select_related и обратной связи related_name ('contacts')."""
        c = Contact.objects.select_related("group", "owner").get(pk=self.c1.pk)
        self.assertEqual(c.group.name, "Работа")
        self.assertEqual(c.owner.username, "testuser")

        # Обратная связь через related_name="contacts"
        work_group_contacts = self.group_work.contacts.all()
        self.assertEqual(work_group_contacts.count(), 2)

    # --------------------------------------------------------------------------
    # 6. Агрегирование и аннотирование (aggregate, annotate, HAVING, NOT IN)
    # --------------------------------------------------------------------------
    def test_aggregation_and_annotation(self):
        """Проверка aggregate(Count, Min, Max), annotate(Count), HAVING и пустых групп."""
        summary = Contact.objects.aggregate(
            total=Count("id"),
            favorites=Count("id", filter=Q(is_favorite=True)),
            oldest=Min("birthday"),
            youngest=Max("birthday"),
        )
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["favorites"], 2)
        self.assertEqual(summary["oldest"], date(1990, 1, 15))
        self.assertEqual(summary["youngest"], date(2005, 11, 5))

        # Аннотирование групп количеством контактов (LEFT JOIN)
        annotated_groups = (
            Group.objects.annotate(cnt=Count("contacts"))
            .order_by("-cnt", "name")
        )
        # Включает группу без контактов с cnt = 0
        empty_g = annotated_groups.get(name="Пустая группа")
        self.assertEqual(empty_g.cnt, 0)

        # Фильтрация по аннотации (аналог HAVING COUNT > 1)
        popular = Group.objects.annotate(cnt=Count("contacts")).filter(cnt__gt=1)
        self.assertEqual(popular.count(), 1)
        self.assertEqual(popular.first().name, "Работа")

        # Пустые группы (contacts__isnull=True)
        empty = Group.objects.filter(contacts__isnull=True)
        self.assertEqual(empty.count(), 1)
        self.assertEqual(empty.first().name, "Пустая группа")

    # --------------------------------------------------------------------------
    # 7. Постраничный вывод (Paginator)
    # --------------------------------------------------------------------------
    def test_pagination(self):
        """Проверка разбиения списка на страницы и обработки некорректного ввода."""
        qs = Contact.objects.order_by("id")
        paginator = Paginator(qs, 2)  # 4 контакта по 2 на страницу = 2 страницы
        self.assertEqual(paginator.num_pages, 2)

        page1 = paginator.get_page(1)
        self.assertEqual(len(page1.object_list), 2)
        self.assertTrue(page1.has_next())
        self.assertFalse(page1.has_previous())

        # Некорректный номер страницы возвращает первую страницу
        invalid_page = paginator.get_page("invalid-page-num")
        self.assertEqual(invalid_page.number, 1)

    # --------------------------------------------------------------------------
    # 8. Проверка веб-представлений (Views)
    # --------------------------------------------------------------------------
    def test_contact_list_view_with_sorting_and_pagination(self):
        """Проверка представления contact_list с сортировкой и пагинатором."""
        self.client.login(username="testuser", password="secretpassword")

        resp = self.client.get(
            reverse("contacts:contact_list"),
            {"sort": "date", "page": "1"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("page_obj", resp.context)
        self.assertEqual(resp.context["sort"], "date")

    def test_statistics_view_orm(self):
        """Проверка представления contact_statistics на Django ORM."""
        resp = self.client.get(reverse("contacts:statistics"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("summary", resp.context)
        self.assertEqual(resp.context["summary"]["total_contacts"], 4)
        self.assertEqual(resp.context["summary"]["favorite_contacts"], 2)
        self.assertIn("popular_groups", resp.context)
        self.assertIn("empty_groups", resp.context)

    def test_search_date_view_orm(self):
        """Проверка представления contact_search_date на ORM с валидацией даты."""
        # 1. Корректная дата
        resp = self.client.get(
            reverse("contacts:search_date"),
            {"date": "1999-12-31"},
        )
        self.assertEqual(resp.status_code, 200)
        contacts = resp.context["contacts"]
        self.assertEqual(len(contacts), 2)  # c1 (1995) и c3 (1990)

        # 2. Некорректная дата
        resp_err = self.client.get(
            reverse("contacts:search_date"),
            {"date": "not-a-valid-date"},
        )
        self.assertEqual(resp_err.status_code, 200)
        self.assertIsNotNone(resp_err.context["error"])
        self.assertContains(resp_err, "Укажите корректную дату")

    def test_contact_detail_404_for_missing_object(self):
        """Проверка возврата ответа 404 при запросе несуществующего контакта."""
        self.client.login(username="testuser", password="secretpassword")
        resp = self.client.get(
            reverse("contacts:contact_detail", kwargs={"pk": 999999})
        )
        self.assertEqual(resp.status_code, 404)
