from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from contacts.models import Contact, Group


class ContactViewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")

        self.group1 = Group.objects.create(name="Работа", owner=self.user1)
        self.group2 = Group.objects.create(name="Семья", owner=self.user2)

        self.contact1 = Contact.objects.create(
            name="Иван",
            firstname="Иванов",
            number=79991112233,
            birthday="1990-01-01",
            owner=self.user1,
            group=self.group1,
            is_favorite=False,
            tags="коллега",
        )
        self.contact2 = Contact.objects.create(
            name="Анна",
            firstname="Смирнова",
            number=79994445566,
            birthday="1995-05-05",
            owner=self.user2,
            group=self.group2,
            is_favorite=True,
        )

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(reverse("contacts:contact_list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp.url)

    def test_contact_list_shows_only_user_contacts(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.get(reverse("contacts:contact_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Иван")
        self.assertNotContains(resp, "Анна")

    def test_search_contacts(self):
        self.client.login(username="user1", password="pass1")
        # поиск по фамилии
        resp = self.client.get(reverse("contacts:contact_list"), {"q": "Иванов"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Иван")

        # поиск по несуществующему слову
        resp = self.client.get(reverse("contacts:contact_list"), {"q": "Ненайденный"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Ничего не найдено")

    def test_favorites_view(self):
        self.client.login(username="user1", password="pass1")
        # У user1 пока нет избранных
        resp = self.client.get(reverse("contacts:favorites"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "В избранном пока нет контактов")

        # Делаем контакт избранным
        self.contact1.is_favorite = True
        self.contact1.save()
        resp = self.client.get(reverse("contacts:favorites"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Иван")

    def test_contact_detail_and_isolation(self):
        self.client.login(username="user1", password="pass1")
        # Свой контакт открывается
        resp = self.client.get(reverse("contacts:contact_detail", kwargs={"pk": self.contact1.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Иван Иванов")

        # Чужой контакт дает 404
        resp = self.client.get(reverse("contacts:contact_detail", kwargs={"pk": self.contact2.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_contact_create(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.post(
            reverse("contacts:contact_create"),
            {
                "name": "Петр",
                "firstname": "Петров",
                "number": 79160001122,
                "birthday": "2000-12-12",
                "group": self.group1.pk,
                "is_favorite": True,
                "tags": "друг",
            },
        )
        self.assertEqual(resp.status_code, 302)
        created = Contact.objects.get(name="Петр", firstname="Петров")
        self.assertEqual(created.owner, self.user1)
        self.assertTrue(created.is_favorite)

    def test_contact_update(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.post(
            reverse("contacts:contact_update", kwargs={"pk": self.contact1.pk}),
            {
                "name": "Иван-Обновленный",
                "firstname": "Иванов",
                "number": 79991112233,
                "birthday": "1990-01-01",
                "group": self.group1.pk,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.contact1.refresh_from_db()
        self.assertEqual(self.contact1.name, "Иван-Обновленный")

    def test_cannot_update_other_user_contact(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.post(
            reverse("contacts:contact_update", kwargs={"pk": self.contact2.pk}),
            {"name": "Взлом"},
        )
        self.assertEqual(resp.status_code, 404)

    def test_contact_delete(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.post(
            reverse("contacts:contact_delete", kwargs={"pk": self.contact1.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Contact.objects.filter(pk=self.contact1.pk).exists())

    def test_cannot_delete_other_user_contact(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.post(
            reverse("contacts:contact_delete", kwargs={"pk": self.contact2.pk})
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Contact.objects.filter(pk=self.contact2.pk).exists())

    def test_toggle_favorite_post(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.post(
            reverse("contacts:toggle_favorite", kwargs={"pk": self.contact1.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.contact1.refresh_from_db()
        self.assertTrue(self.contact1.is_favorite)

    def test_groups_crud_and_isolation(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.get(reverse("contacts:group_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Работа")
        self.assertNotContains(resp, "Семья")

        # Создание группы
        resp = self.client.post(
            reverse("contacts:group_create"),
            {"name": "Спорт", "description": "Тренировки"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Group.objects.filter(name="Спорт", owner=self.user1).exists())

        # Удаление группы
        sport_group = Group.objects.get(name="Спорт", owner=self.user1)
        resp = self.client.post(
            reverse("contacts:group_delete", kwargs={"pk": sport_group.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Group.objects.filter(pk=sport_group.pk).exists())

    def test_home_view_anonymous(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "KeepInTouch")
        self.assertContains(resp, "Зарегистрироваться")

    def test_home_view_authenticated(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Все контакты")
        self.assertContains(resp, "Иван Иванов")
        self.assertEqual(resp.context["total_contacts"], 1)

    def test_contact_form_context_has_existing_tags(self):
        self.client.login(username="user1", password="pass1")
        resp = self.client.get(reverse("contacts:contact_create"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("existing_tags", resp.context)
        self.assertIn("коллега", resp.context["existing_tags"])

