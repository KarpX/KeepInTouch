from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsTests(TestCase):
    def test_register_get(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Регистрация")

    def test_register_post_success(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "ivan_test",
                "email": "ivan@example.com",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="ivan_test").exists())
        # Проверяем, что пользователь авторизован после регистрации
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="ivan_test").pk)

    def test_login_and_logout(self):
        user = User.objects.create_user(username="testlogin", password="PassWord123!")
        login_resp = self.client.post(
            reverse("accounts:login"),
            {"username": "testlogin", "password": "PassWord123!"},
        )
        self.assertEqual(login_resp.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

        logout_resp = self.client.post(reverse("accounts:logout"))
        self.assertEqual(logout_resp.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
