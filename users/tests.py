from django.contrib.auth import get_user
from users.models import CustomUser
from django.test import TestCase
from django.urls import reverse


class RegistrationTestCase(TestCase):
    def test_user_account_is_created(self):
        self.client.post(
            reverse("users:register"),
            data={
                "username": "hamidbek2669",
                "first_name": "Hamid",
                "last_name": "Esbergenov",
                "email": "hamidesbergenov@gmail.com",
                "password": "somepassword"
            }
        )
        user = CustomUser.objects.get(username="hamidbek2669")

        self.assertEqual(user.first_name, "Hamid")
        self.assertEqual(user.last_name, "Esbergenov")
        self.assertEqual(user.email, "hamidesbergenov@gmail.com")
        self.assertNotEqual(user.password, "somepassword")
        self.assertTrue(user.check_password("somepassword"))

    def test_required_fields(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "first_name": "Hamid",
                "email": "hamidesbergenov@gmail.com"
            }
        )
        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "password", "This field is required.")

    def test_invalid_email(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "hamidbek2669",
                "first_name": "Hamid",
                "last_name": "Esbergenov",
                "email": "invalid-email",
                "password": "somepassword"
            }
        )
        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")

    def test_unique_username(self):
        # 1. create a user
        user = CustomUser.objects.create(username = "hamidbek2669", first_name = "Hamid")
        user.set_password("somepass")
        user.save()

        # 2. try to create another user with that same username
        response = self.client.post(
            reverse("users:register"),
            data = {
                "username": "hamidbek2669",
                "first_name": "Hamid",
                "last_name": "Esbergenov",
                "email": "hamidesbergenov@gmail.com",
                "password": "somepassword"
            }
        )

        # 3. check that the second user was not created
        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 1)

        # 4. check that the form contains the error message
        self.assertFormError(response, "form", "username", "A user with that username already exists.")


class LoginTestCase(TestCase):
    # DRY = Don't Repeat Yourself
    def setUp(self):
        self.db_user = CustomUser.objects.create(username="hamidbek2669", first_name="Hamid")
        self.db_user.set_password("somepass")
        self.db_user.save()

    def test_successful_login(self):

        self.client.post(
            reverse("users:login"),
            data={
                "username": "hamidbek2669",
                "password": "somepass"
            }
        )

        user = get_user(self.client)

        self.assertTrue(user.is_authenticated)

    def test_wrong_credentials(self):


        self.client.post(
            reverse("users:login"),
            data={
                "username": "wrong_username",
                "password": "somepass"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.client.post(
            reverse("users:login"),
            data={
                "username": "wrong_username",
                "password": "wrong_password"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout(self):


        self.client.login(username="hamidbek2669", password="somepass")

        self.client.get(reverse("users:logout"))

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)


class ProfileTestCase(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:login") + "?next=/users/profile/")

    def test_profile_details(self):
        user = CustomUser.objects.create(
            username="hamidbek2669", first_name="Hamid", last_name="Esbergenov", email="hamidesbergenov@gmail.com"
        )
        user.set_password("somepass")
        user.save()

        self.client.login(username="hamidbek2669", password="somepass")

        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.email)

    def test_update_profile(self):
        user = CustomUser.objects.create(
            username="hamidbek2669", first_name="Hamid", last_name="Esbergenov", email="hamidesbergenov@gmail.com"
        )
        user.set_password("somepass")
        user.save()

        self.client.login(username="hamidbek2669", password="somepass")

        response = self.client.post(
            reverse("users:profile-edit"),
            data={
                "username": "hamidbek2669",
                "first_name": "Hamid",
                "last_name": "Yesbergenov",
                "email": "esbergenovhamid@gmail.com"
            }
        )

        user = CustomUser.objects.get(pk=user.pk)

        self.assertEqual(user.last_name, "Yesbergenov")
        self.assertEqual(user.email, "esbergenovhamid@gmail.com")
        self.assertEqual(response.url, reverse("users:profile"))




