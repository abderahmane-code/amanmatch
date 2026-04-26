import io
from datetime import date

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from PIL import Image

from accounts.models import AccountProfile
from verification.admin import approve_verifications, reject_verifications
from verification.models import IdentityVerification


def _make_image(name="test.jpg"):
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color="red").save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/jpeg")


class VerificationAccessTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_anonymous_redirected_from_start(self):
        response = self.client.get(reverse("verification:start"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_anonymous_redirected_from_status(self):
        response = self.client.get(reverse("verification:status"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class VerificationSubmitTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="verifyuser", password="TestPass123!"
        )
        AccountProfile.objects.create(
            user=self.user,
            gender="M",
            date_of_birth=date(1990, 1, 1),
            country="France",
            city="Paris",
        )
        self.client.login(username="verifyuser", password="TestPass123!")
        self.url = reverse("verification:start")

    def test_logged_in_user_can_submit(self):
        response = self.client.post(
            self.url,
            {
                "document_image": _make_image("doc.jpg"),
                "selfie_image": _make_image("selfie.jpg"),
                "confirmation": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            IdentityVerification.objects.filter(user=self.user).exists()
        )

    def test_checkbox_required(self):
        response = self.client.post(
            self.url,
            {
                "document_image": _make_image("doc.jpg"),
                "selfie_image": _make_image("selfie.jpg"),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            IdentityVerification.objects.filter(user=self.user).exists()
        )

    def test_duplicate_pending_blocked(self):
        self.client.post(
            self.url,
            {
                "document_image": _make_image("doc.jpg"),
                "selfie_image": _make_image("selfie.jpg"),
                "confirmation": "on",
            },
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            IdentityVerification.objects.filter(user=self.user).count(), 1
        )

    def test_match_score_stored(self):
        self.client.post(
            self.url,
            {
                "document_image": _make_image("doc.jpg"),
                "selfie_image": _make_image("selfie.jpg"),
                "confirmation": "on",
            },
        )
        v = IdentityVerification.objects.get(user=self.user)
        self.assertEqual(v.match_score, 0.87)
        self.assertEqual(v.auto_result, "possible_match")
        self.assertEqual(v.status, "pending")


class VerificationStatusTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="statususer", password="TestPass123!"
        )
        AccountProfile.objects.create(
            user=self.user,
            gender="F",
            date_of_birth=date(1992, 5, 10),
            country="UK",
            city="London",
        )
        self.client.login(username="statususer", password="TestPass123!")

    def test_status_page_shows_pending(self):
        self.client.post(
            reverse("verification:start"),
            {
                "document_image": _make_image("doc.jpg"),
                "selfie_image": _make_image("selfie.jpg"),
                "confirmation": "on",
            },
        )
        response = self.client.get(reverse("verification:status"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending review")

    def test_status_page_no_request(self):
        response = self.client.get(reverse("verification:status"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Start identity verification")


class AdminActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admintest", password="TestPass123!"
        )
        self.account = AccountProfile.objects.create(
            user=self.user,
            gender="M",
            date_of_birth=date(1988, 3, 20),
            country="Germany",
            city="Berlin",
        )
        self.verification = IdentityVerification.objects.create(
            user=self.user,
            document_image="verification/documents/test.jpg",
            selfie_image="verification/selfies/test.jpg",
            status="pending",
            match_score=0.87,
            auto_result="possible_match",
        )
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser(
            username="admin", password="AdminPass123!"
        )

    def test_approve_action(self):
        request = self.factory.post("/admin/")
        request.user = self.admin_user
        qs = IdentityVerification.objects.filter(pk=self.verification.pk)
        approve_verifications(None, request, qs)
        self.verification.refresh_from_db()
        self.account.refresh_from_db()
        self.assertEqual(self.verification.status, "approved")
        self.assertIsNotNone(self.verification.reviewed_at)
        self.assertTrue(self.account.is_identity_verified)

    def test_reject_action(self):
        request = self.factory.post("/admin/")
        request.user = self.admin_user
        qs = IdentityVerification.objects.filter(pk=self.verification.pk)
        reject_verifications(None, request, qs)
        self.verification.refresh_from_db()
        self.account.refresh_from_db()
        self.assertEqual(self.verification.status, "rejected")
        self.assertIsNotNone(self.verification.reviewed_at)
        self.assertFalse(self.account.is_identity_verified)
        self.assertEqual(
            self.verification.rejection_reason,
            "Verification rejected by staff review.",
        )


class DashboardVerificationIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="dashverify", password="TestPass123!"
        )
        AccountProfile.objects.create(
            user=self.user,
            gender="F",
            date_of_birth=date(1995, 8, 1),
            country="Morocco",
            city="Rabat",
        )
        self.client.login(username="dashverify", password="TestPass123!")

    def test_dashboard_shows_pending_status(self):
        self.client.post(
            reverse("verification:start"),
            {
                "document_image": _make_image("doc.jpg"),
                "selfie_image": _make_image("selfie.jpg"),
                "confirmation": "on",
            },
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending review")
        self.assertContains(response, "View verification status")
