from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class MatchmakingProfile(models.Model):
    MARITAL_STATUS_CHOICES = [
        ("single", _("Single")),
        ("divorced", _("Divorced")),
        ("widowed", _("Widowed")),
    ]

    INTENTION_CHOICES = [
        ("marriage_soon", _("Marriage soon")),
        ("marriage_later", _("Marriage later")),
        ("family_discussion", _("Family discussion needed")),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matchmaking_profile",
    )

    # Basic public matchmaking info
    marital_status = models.CharField(
        max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, default=""
    )
    education_level = models.CharField(max_length=100, blank=True, default="")
    profession = models.CharField(max_length=100, blank=True, default="")
    short_bio = models.TextField(blank=True, default="")
    serious_intention = models.CharField(
        max_length=30, choices=INTENTION_CHOICES, blank=True, default=""
    )

    # Partner preferences
    preferred_age_min = models.PositiveIntegerField(null=True, blank=True)
    preferred_age_max = models.PositiveIntegerField(null=True, blank=True)
    preferred_country = models.CharField(max_length=100, blank=True, default="")
    preferred_city = models.CharField(max_length=100, blank=True, default="")
    preferred_education_level = models.CharField(max_length=100, blank=True, default="")
    important_values = models.TextField(blank=True, default="")

    # Privacy settings
    show_photo = models.BooleanField(default=False)
    show_city = models.BooleanField(default=True)
    show_profession = models.BooleanField(default=True)
    private_mode = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    COMPLETION_FIELDS = [
        "marital_status",
        "education_level",
        "profession",
        "short_bio",
        "serious_intention",
        "preferred_age_min",
        "preferred_age_max",
        "important_values",
    ]

    class Meta:
        verbose_name = _("Matchmaking Profile")
        verbose_name_plural = _("Matchmaking Profiles")

    def __str__(self):
        return f"{self.user.username} — {self.get_marital_status_display() or 'Incomplete'}"

    @property
    def completion_percentage(self):
        filled = 0
        for field_name in self.COMPLETION_FIELDS:
            value = getattr(self, field_name)
            if value is not None and value != "":
                filled += 1
        return int((filled / len(self.COMPLETION_FIELDS)) * 100)
