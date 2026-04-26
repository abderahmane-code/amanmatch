from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountProfile(models.Model):
    GENDER_CHOICES = [
        ("M", _("Male")),
        ("F", _("Female")),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_profile",
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    is_identity_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Account Profile")
        verbose_name_plural = _("Account Profiles")

    def __str__(self):
        return f"{self.user.username} — {self.get_gender_display()}, {self.country}"
