from django.test import TestCase
from django.contrib.auth.models import User
from contacts.forms import ContactForm, GroupForm
from contacts.models import Group


class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="p1")
        self.other_user = User.objects.create_user(username="u2", password="p2")
        self.my_group = Group.objects.create(name="Моя группа", owner=self.user)
        self.other_group = Group.objects.create(name="Чужая группа", owner=self.other_user)

    def test_contact_form_filters_groups_by_user(self):
        form = ContactForm(user=self.user)
        self.assertIn(self.my_group, form.fields["group"].queryset)
        self.assertNotIn(self.other_group, form.fields["group"].queryset)

    def test_contact_form_valid(self):
        data = {
            "name": "Тест",
            "firstname": "Тестов",
            "number": 79001234567,
            "birthday": "2000-01-01",
            "group": self.my_group.pk,
            "is_favorite": True,
            "tags": "работа",
        }
        form = ContactForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_group_form_valid(self):
        data = {"name": "Новая", "description": "Описание"}
        form = GroupForm(data=data)
        self.assertTrue(form.is_valid())
