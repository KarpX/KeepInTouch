from django.test import TestCase
from django.contrib.auth.models import User
from contacts.models import Contact, Group


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.group = Group.objects.create(
            name="Друзья",
            description="Круг общения",
            owner=self.user,
        )
        self.contact = Contact.objects.create(
            name="Никита",
            firstname="Малютин",
            number=79161234567,
            birthday="2006-05-15",
            owner=self.user,
            group=self.group,
            is_favorite=False,
            tags="школа, спорт",
        )

    def test_group_str(self):
        self.assertEqual(str(self.group), "Друзья")

    def test_contact_str(self):
        self.assertEqual(str(self.contact), "Никита Малютин")

    def test_toggle_favorite(self):
        self.assertFalse(self.contact.is_favorite)
        self.contact.toggle_favorite()
        self.contact.refresh_from_db()
        self.assertTrue(self.contact.is_favorite)
        self.contact.toggle_favorite()
        self.contact.refresh_from_db()
        self.assertFalse(self.contact.is_favorite)

    def test_matches_query(self):
        self.assertTrue(self.contact.matches("никита"))
        self.assertTrue(self.contact.matches("малютин"))
        self.assertTrue(self.contact.matches("79161234567"))
        self.assertTrue(self.contact.matches("друзья"))
        self.assertTrue(self.contact.matches("спорт"))
        self.assertFalse(self.contact.matches("несуществующий"))

    def test_tag_list(self):
        self.assertEqual(self.contact.tag_list, ["школа", "спорт"])
