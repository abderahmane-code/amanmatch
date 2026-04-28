from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountProfile
from matchmaking.models import Interest, Match
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


# =====================================================================
# Mutual Interest System Tests
# =====================================================================


class SendInterestTests(TestCase, MatchmakingTestMixin):
    def setUp(self):
        self.verified = self.create_user_with_profiles(
            "verified_sender", is_verified=True
        )
        self.unverified = self.create_user_with_profiles(
            "unverified_sender", is_verified=False
        )
        self.receiver = self.create_user_with_profiles("receiver")

    def test_unverified_cannot_send_interest(self):
        self.client.login(username="unverified_sender", password="TestPass123!")
        resp = self.client.post(
            reverse("matchmaking:send_interest", args=[self.receiver.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Interest.objects.exists())

    def test_verified_can_send_interest(self):
        self.client.login(username="verified_sender", password="TestPass123!")
        resp = self.client.post(
            reverse("matchmaking:send_interest", args=[self.receiver.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            Interest.objects.filter(
                sender=self.verified, receiver=self.receiver, status="pending"
            ).exists()
        )

    def test_cannot_send_interest_to_self(self):
        self.client.login(username="verified_sender", password="TestPass123!")
        resp = self.client.post(
            reverse("matchmaking:send_interest", args=[self.verified.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Interest.objects.exists())

    def test_duplicate_pending_blocked(self):
        self.client.login(username="verified_sender", password="TestPass123!")
        Interest.objects.create(
            sender=self.verified, receiver=self.receiver, status="pending"
        )
        self.client.post(
            reverse("matchmaking:send_interest", args=[self.receiver.pk])
        )
        self.assertEqual(
            Interest.objects.filter(
                sender=self.verified, receiver=self.receiver
            ).count(),
            1,
        )

    def test_anonymous_cannot_send(self):
        resp = self.client.post(
            reverse("matchmaking:send_interest", args=[self.receiver.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)


class AcceptRejectInterestTests(TestCase, MatchmakingTestMixin):
    def setUp(self):
        self.sender = self.create_user_with_profiles("sender", is_verified=True)
        self.receiver = self.create_user_with_profiles("receiver", is_verified=True)
        self.interest = Interest.objects.create(
            sender=self.sender, receiver=self.receiver
        )

    def test_receiver_can_accept(self):
        self.client.login(username="receiver", password="TestPass123!")
        resp = self.client.post(
            reverse("matchmaking:accept_interest", args=[self.interest.pk])
        )
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, "accepted")
        self.assertTrue(
            Match.objects.filter(user1=self.sender, user2=self.receiver).exists()
        )

    def test_accepting_creates_match(self):
        self.client.login(username="receiver", password="TestPass123!")
        self.client.post(
            reverse("matchmaking:accept_interest", args=[self.interest.pk])
        )
        self.assertEqual(Match.objects.count(), 1)

    def test_duplicate_match_not_created(self):
        Match.objects.create(user1=self.sender, user2=self.receiver)
        self.client.login(username="receiver", password="TestPass123!")
        self.client.post(
            reverse("matchmaking:accept_interest", args=[self.interest.pk])
        )
        self.assertEqual(Match.objects.count(), 1)

    def test_receiver_can_reject(self):
        self.client.login(username="receiver", password="TestPass123!")
        self.client.post(
            reverse("matchmaking:reject_interest", args=[self.interest.pk])
        )
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, "rejected")

    def test_sender_cannot_accept_own_sent(self):
        self.client.login(username="sender", password="TestPass123!")
        resp = self.client.post(
            reverse("matchmaking:accept_interest", args=[self.interest.pk])
        )
        self.assertEqual(resp.status_code, 403)
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, "pending")

    def test_sender_cannot_reject_own_sent(self):
        self.client.login(username="sender", password="TestPass123!")
        resp = self.client.post(
            reverse("matchmaking:reject_interest", args=[self.interest.pk])
        )
        self.assertEqual(resp.status_code, 403)
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, "pending")


class InterestListAccessTests(TestCase, MatchmakingTestMixin):
    def test_received_requires_login(self):
        resp = self.client.get(reverse("matchmaking:received_interests"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_sent_requires_login(self):
        resp = self.client.get(reverse("matchmaking:sent_interests"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_matches_requires_login(self):
        resp = self.client.get(reverse("matchmaking:matches"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_logged_in_can_access_received(self):
        user = self.create_user_with_profiles("user1")
        self.client.login(username="user1", password="TestPass123!")
        resp = self.client.get(reverse("matchmaking:received_interests"))
        self.assertEqual(resp.status_code, 200)

    def test_logged_in_can_access_sent(self):
        user = self.create_user_with_profiles("user1")
        self.client.login(username="user1", password="TestPass123!")
        resp = self.client.get(reverse("matchmaking:sent_interests"))
        self.assertEqual(resp.status_code, 200)


class ProfileDetailMatchedTests(TestCase, MatchmakingTestMixin):
    def test_matched_shows_matched_badge(self):
        sender = self.create_user_with_profiles("sender", is_verified=True)
        receiver = self.create_user_with_profiles("receiver", is_verified=True)
        Interest.objects.create(
            sender=sender, receiver=receiver, status="accepted"
        )
        Match.objects.create(user1=sender, user2=receiver)
        self.client.login(username="sender", password="TestPass123!")
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[receiver.pk])
        )
        self.assertContains(resp, "Matched")
        self.assertContains(resp, "Messaging will be available in the next step.")

    def test_private_mode_remains_before_match(self):
        viewer = self.create_user_with_profiles("viewer", is_verified=True)
        private_user = self.create_user_with_profiles(
            "priv", private_mode=True, city="SecretCity",
            profession="SecretJob", short_bio="Hidden bio",
            important_values="Hidden values",
        )
        self.client.login(username="viewer", password="TestPass123!")
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[private_user.pk])
        )
        self.assertNotContains(resp, "SecretCity")
        self.assertNotContains(resp, "SecretJob")
        self.assertNotContains(resp, "Hidden bio")
        self.assertNotContains(resp, "Hidden values")
        self.assertContains(resp, "Private profile")

    def test_private_mode_relaxed_after_match(self):
        viewer = self.create_user_with_profiles("viewer", is_verified=True)
        private_user = self.create_user_with_profiles(
            "priv", private_mode=True, city="SecretCity",
            profession="SecretJob", short_bio="Hidden bio",
            important_values="Hidden values",
        )
        Match.objects.create(user1=viewer, user2=private_user)
        self.client.login(username="viewer", password="TestPass123!")
        resp = self.client.get(
            reverse("matchmaking:public_profile", args=[private_user.pk])
        )
        self.assertContains(resp, "SecretCity")
        self.assertContains(resp, "SecretJob")
        self.assertContains(resp, "Hidden bio")
        self.assertContains(resp, "Hidden values")


class InterestPagePrivacyTests(TestCase, MatchmakingTestMixin):
    def test_received_does_not_expose_email(self):
        sender = self.create_user_with_profiles(
            "sender", email="secret@mail.com", is_verified=True
        )
        receiver = self.create_user_with_profiles("receiver")
        Interest.objects.create(sender=sender, receiver=receiver)
        self.client.login(username="receiver", password="TestPass123!")
        resp = self.client.get(reverse("matchmaking:received_interests"))
        self.assertNotContains(resp, "secret@mail.com")

    def test_sent_does_not_expose_email(self):
        sender = self.create_user_with_profiles("sender", is_verified=True)
        receiver = self.create_user_with_profiles(
            "receiver", email="secret2@mail.com"
        )
        Interest.objects.create(sender=sender, receiver=receiver)
        self.client.login(username="sender", password="TestPass123!")
        resp = self.client.get(reverse("matchmaking:sent_interests"))
        self.assertNotContains(resp, "secret2@mail.com")

    def test_matches_does_not_expose_email(self):
        u1 = self.create_user_with_profiles("user1", is_verified=True)
        u2 = self.create_user_with_profiles(
            "user2", email="hidden@mail.com", is_verified=True
        )
        Match.objects.create(user1=u1, user2=u2)
        self.client.login(username="user1", password="TestPass123!")
        resp = self.client.get(reverse("matchmaking:matches"))
        self.assertNotContains(resp, "hidden@mail.com")
