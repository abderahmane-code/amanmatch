from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import AccountProfile
from profiles.models import MatchmakingProfile


class MatchmakingProfileCreationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("accounts:register")
        self.adult_dob = (date.today() - timedelta(days=365 * 25)).isoformat()
        self.valid_data = {
            "username": "profileuser",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
            "gender": "F",
            "date_of_birth": self.adult_dob,
            "country": "France",
            "city": "Paris",
            "phone_number": "",
        }

    def test_matchmaking_profile_created_on_registration(self):
        self.client.post(self.register_url, self.valid_data)
        user = User.objects.get(username="profileuser")
        self.assertTrue(hasattr(user, "matchmaking_profile"))
        profile = user.matchmaking_profile
        self.assertFalse(profile.private_mode)
        self.assertEqual(profile.completion_percentage, 0)


class ProfileDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="detailuser",
            password="TestPass123!",
            first_name="Ali",
            last_name="Hassan",
            email="ali@example.com",
        )
        self.account = AccountProfile.objects.create(
            user=self.user,
            gender="M",
            date_of_birth=date(1995, 6, 15),
            country="Morocco",
            city="Rabat",
            phone_number="+212600000000",
        )
        self.profile = MatchmakingProfile.objects.create(
            user=self.user,
            marital_status="single",
            profession="Engineer",
        )
        self.url = reverse("profiles:detail")

    def test_logged_in_user_can_access(self):
        self.client.login(username="detailuser", password="TestPass123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ali")

    def test_anonymous_user_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_does_not_expose_email(self):
        self.client.login(username="detailuser", password="TestPass123!")
        response = self.client.get(self.url)
        self.assertNotContains(response, "ali@example.com")

    def test_does_not_expose_phone(self):
        self.client.login(username="detailuser", password="TestPass123!")
        response = self.client.get(self.url)
        self.assertNotContains(response, "+212600000000")


class ProfileEditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="edituser", password="TestPass123!"
        )
        self.account = AccountProfile.objects.create(
            user=self.user,
            gender="M",
            date_of_birth=date(1990, 1, 1),
            country="UK",
            city="London",
        )
        self.profile = MatchmakingProfile.objects.create(user=self.user)
        self.url = reverse("profiles:edit")

    def test_logged_in_user_can_access(self):
        self.client.login(username="edituser", password="TestPass123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_can_update_profile(self):
        self.client.login(username="edituser", password="TestPass123!")
        response = self.client.post(self.url, {
            "marital_status": "single",
            "education_level": "Master",
            "profession": "Doctor",
            "short_bio": "Looking for a serious partner.",
            "serious_intention": "marriage_soon",
            "preferred_age_min": "25",
            "preferred_age_max": "35",
            "preferred_country": "",
            "preferred_city": "",
            "preferred_education_level": "",
            "important_values": "Honesty, Family",
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.marital_status, "single")
        self.assertEqual(self.profile.profession, "Doctor")
        self.assertEqual(self.profile.serious_intention, "marriage_soon")


class DashboardCompletionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="compuser", password="TestPass123!"
        )
        self.account = AccountProfile.objects.create(
            user=self.user,
            gender="F",
            date_of_birth=date(1992, 3, 10),
            country="Germany",
            city="Berlin",
        )
        self.profile = MatchmakingProfile.objects.create(user=self.user)
        self.client.login(username="compuser", password="TestPass123!")

    def test_dashboard_shows_completion_percentage(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "0%")

    def test_dashboard_shows_updated_completion(self):
        self.profile.marital_status = "single"
        self.profile.education_level = "PhD"
        self.profile.profession = "Researcher"
        self.profile.short_bio = "I am a researcher."
        self.profile.save()
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "50%")
