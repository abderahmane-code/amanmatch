from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import AccountProfile


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("accounts:register")
        self.adult_dob = (date.today() - timedelta(days=365 * 25)).isoformat()
        self.minor_dob = (date.today() - timedelta(days=365 * 16)).isoformat()
        self.valid_data = {
            "username": "testuser1",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
            "gender": "M",
            "date_of_birth": self.adult_dob,
            "country": "Morocco",
            "city": "Casablanca",
            "phone_number": "",
        }

    def test_adult_can_register(self):
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser1").exists())

    def test_under_18_cannot_register(self):
        data = self.valid_data.copy()
        data["date_of_birth"] = self.minor_dob
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "You must be at least 18 years old to use AmanMatch."
        )
        self.assertFalse(User.objects.filter(username="testuser1").exists())

    def test_profile_created_after_registration(self):
        self.client.post(self.register_url, self.valid_data)
        user = User.objects.get(username="testuser1")
        self.assertTrue(hasattr(user, "account_profile"))
        profile = user.account_profile
        self.assertEqual(profile.gender, "M")
        self.assertEqual(profile.country, "Morocco")
        self.assertEqual(profile.city, "Casablanca")
        self.assertFalse(profile.is_identity_verified)

    def test_user_logged_in_after_registration(self):
        response = self.client.post(self.register_url, self.valid_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration_redirects_to_dashboard(self):
        response = self.client.post(self.register_url, self.valid_data)
        self.assertRedirects(response, reverse("dashboard"))


class DashboardVerificationStatusTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="dashuser", password="TestPass123!"
        )
        self.profile = AccountProfile.objects.create(
            user=self.user,
            gender="F",
            date_of_birth=date(1995, 1, 1),
            country="France",
            city="Paris",
        )
        self.client.login(username="dashuser", password="TestPass123!")

    def test_dashboard_shows_not_verified(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Not verified")
        self.assertContains(
            response, "Complete identity verification to unlock matchmaking."
        )

    def test_dashboard_shows_verified(self):
        self.profile.is_identity_verified = True
        self.profile.save()
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Verified")
        self.assertContains(response, "Your identity has been verified.")


class VerificationStartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("verification:start")

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_shows_verification_form(self):
        user = User.objects.create_user(
            username="verifyuser", password="TestPass123!"
        )
        self.client.login(username="verifyuser", password="TestPass123!")
        response = self.client.get(self.url)
        self.assertContains(response, "Identity Verification")
