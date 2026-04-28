from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountProfile
from profiles.models import MatchmakingProfile


class MatchmakingTestMixin:
    """Shared helpers for creating test users with both profiles."""

    def create_user_with_profiles(
        self,
        username,
        first_name="Test",
        gender="M",
        country="Morocco",
        city="Casablanca",
        age=25,
        is_verified=False,
        marital_status="single",
        education_level="Masters",
        profession="Engineer",
        serious_intention="marriage_soon",
        short_bio="A short bio.",
        important_values="Honesty",
        private_mode=False,
        show_city=True,
        show_profession=True,
        email="",
        phone_number="",
    ):
        dob = date.today() - timedelta(days=age * 365 + 100)
        user = User.objects.create_user(
            username=username,
            password="TestPass123!",
            first_name=first_name,
            email=email or f"{username}@example.com",
        )
        AccountProfile.objects.create(
            user=user,
            gender=gender,
            date_of_birth=dob,
            country=country,
            city=city,
            phone_number=phone_number,
            is_identity_verified=is_verified,
        )
        MatchmakingProfile.objects.create(
            user=user,
            marital_status=marital_status,
            education_level=education_level,
            profession=profession,
            short_bio=short_bio,
            serious_intention=serious_intention,
            important_values=important_values,
            private_mode=private_mode,
            show_city=show_city,
            show_profession=show_profession,
        )
        return user


class SearchAccessTests(TestCase, MatchmakingTestMixin):
    def test_anonymous_redirected(self):
        resp = self.client.get(reverse("matchmaking:search"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_logged_in_can_access(self):
        user = self.create_user_with_profiles("viewer")
        self.client.login(username="viewer", password="TestPass123!")
        resp = self.client.get(reverse("matchmaking:search"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Find your")

    def test_excludes_current_user(self):
        me = self.create_user_with_profiles("me", first_name="MeUser")
        other = self.create_user_with_profiles("other", first_name="OtherUser")
        self.client.login(username="me", password="TestPass123!")
        resp = self.client.get(reverse("matchmaking:search"))
        self.assertContains(resp, "OtherUser")
        self.assertNotContains(resp, "MeUser")


class SearchFilterTests(TestCase, MatchmakingTestMixin):
    def setUp(self):
        self.viewer = self.create_user_with_profiles("viewer")
        self.client.login(username="viewer", password="TestPass123!")

        self.male = self.create_user_with_profiles(
            "male1", first_name="Ahmed", gender="M", country="Morocco",
            city="Casablanca", age=30, marital_status="single",
            education_level="Masters", serious_intention="marriage_soon",
        )
        self.female = self.create_user_with_profiles(
            "female1", first_name="Fatima", gender="F", country="France",
            city="Paris", age=28, marital_status="divorced",
            education_level="PhD", serious_intention="marriage_later",
        )

    def test_filter_by_gender(self):
        resp = self.client.get(reverse("matchmaking:search"), {"gender": "F"})
        self.assertContains(resp, "Fatima")
        self.assertNotContains(resp, "Ahmed")

    def test_filter_by_country(self):
        resp = self.client.get(reverse("matchmaking:search"), {"country": "France"})
        self.assertContains(resp, "Fatima")
        self.assertNotContains(resp, "Ahmed")

    def test_filter_by_city(self):
        resp = self.client.get(reverse("matchmaking:search"), {"city": "Paris"})
        self.assertContains(resp, "Fatima")
        self.assertNotContains(resp, "Ahmed")

    def test_filter_by_age_range(self):
        resp = self.client.get(reverse("matchmaking:search"), {"age_min": "29", "age_max": "35"})
        self.assertContains(resp, "Ahmed")
        self.assertNotContains(resp, "Fatima")

    def test_filter_by_marital_status(self):
        resp = self.client.get(reverse("matchmaking:search"), {"marital_status": "divorced"})
        self.assertContains(resp, "Fatima")
        self.assertNotContains(resp, "Ahmed")

    def test_filter_by_education(self):
        resp = self.client.get(reverse("matchmaking:search"), {"education_level": "PhD"})
        self.assertContains(resp, "Fatima")
        self.assertNotContains(resp, "Ahmed")

    def test_filter_by_intention(self):
        resp = self.client.get(reverse("matchmaking:search"), {"serious_intention": "marriage_later"})
        self.assertContains(resp, "Fatima")
        self.assertNotContains(resp, "Ahmed")


class SearchPrivacyTests(TestCase, MatchmakingTestMixin):
    def setUp(self):
        self.viewer = self.create_user_with_profiles("viewer")
        self.client.login(username="viewer", password="TestPass123!")

    def test_cards_do_not_expose_email(self):
        self.create_user_with_profiles("target", email="secret@example.com")
        resp = self.client.get(reverse("matchmaking:search"))
        self.assertNotContains(resp, "secret@example.com")

    def test_cards_do_not_expose_phone(self):
        self.create_user_with_profiles("target", phone_number="+212612345678")
        resp = self.client.get(reverse("matchmaking:search"))
        self.assertNotContains(resp, "+212612345678")

    def test_private_mode_hides_city_and_profession(self):
        self.create_user_with_profiles(
            "private_user", first_name="Secret",
            city="HiddenCity", profession="HiddenJob",
            private_mode=True,
        )
        resp = self.client.get(reverse("matchmaking:search"))
        self.assertNotContains(resp, "HiddenCity")
        self.assertNotContains(resp, "HiddenJob")
        self.assertContains(resp, "Private profile")


class ProfileDetailTests(TestCase, MatchmakingTestMixin):
    def setUp(self):
        self.viewer = self.create_user_with_profiles("viewer")
        self.target = self.create_user_with_profiles(
            "target", first_name="TargetUser",
            email="target@secret.com", phone_number="+212699999999",
            short_bio="Great person", important_values="Honesty",
        )
        self.client.login(username="viewer", password="TestPass123!")

    def test_anonymous_redirected(self):
        self.client.logout()
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[self.target.pk])
        )
        self.assertEqual(resp.status_code, 302)

    def test_logged_in_can_access(self):
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[self.target.pk])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "TargetUser")

    def test_does_not_expose_email(self):
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[self.target.pk])
        )
        self.assertNotContains(resp, "target@secret.com")

    def test_does_not_expose_phone(self):
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[self.target.pk])
        )
        self.assertNotContains(resp, "+212699999999")

    def test_does_not_expose_date_of_birth(self):
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[self.target.pk])
        )
        dob = self.target.account_profile.date_of_birth
        self.assertNotContains(resp, str(dob))

    def test_private_mode_hides_bio_and_values(self):
        private_user = self.create_user_with_profiles(
            "priv", first_name="PrivUser",
            short_bio="Secret bio", important_values="Secret values",
            private_mode=True, city="HiddenCity", profession="HiddenJob",
        )
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[private_user.pk])
        )
        self.assertNotContains(resp, "Secret bio")
        self.assertNotContains(resp, "Secret values")
        self.assertNotContains(resp, "HiddenCity")
        self.assertNotContains(resp, "HiddenJob")
        self.assertContains(resp, "Private profile")


class InterestButtonTests(TestCase, MatchmakingTestMixin):
    def setUp(self):
        self.target = self.create_user_with_profiles("target", first_name="Target")

    def test_unverified_sees_verification_message(self):
        unverified = self.create_user_with_profiles("unverified", is_verified=False)
        self.client.login(username="unverified", password="TestPass123!")
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[self.target.pk])
        )
        self.assertContains(resp, "Verify your identity to send interest.")
        self.assertNotContains(resp, "Send interest")

    def test_verified_sees_send_interest(self):
        verified = self.create_user_with_profiles("verified", is_verified=True)
        self.client.login(username="verified", password="TestPass123!")
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[self.target.pk])
        )
        self.assertContains(resp, "Send interest")
