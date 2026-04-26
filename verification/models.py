from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class IdentityVerification(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    AUTO_RESULT_CHOICES = [
        ("not_checked", _("Not checked")),
        ("possible_match", _("Possible match")),
        ("possible_mismatch", _("Possible mismatch")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="identity_verifications",
    )
    document_image = models.ImageField(upload_to="verification/documents/")
    selfie_image = models.ImageField(upload_to="verification/selfies/")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")
    match_score = models.FloatField(null=True, blank=True)
    provider_response = models.JSONField(null=True, blank=True)
    auto_result = models.CharField(
        max_length=20, choices=AUTO_RESULT_CHOICES, default="not_checked"
    )

    class Meta:
        verbose_name = _("Identity Verification")
        verbose_name_plural = _("Identity Verifications")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user.username} — {self.get_status_display()}"
