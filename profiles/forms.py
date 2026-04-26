from django import forms
from django.utils.translation import gettext_lazy as _

from profiles.models import MatchmakingProfile


class MatchmakingProfileForm(forms.ModelForm):
    class Meta:
        model = MatchmakingProfile
        fields = [
            "marital_status",
            "education_level",
            "profession",
            "short_bio",
            "serious_intention",
            "preferred_age_min",
            "preferred_age_max",
            "preferred_country",
            "preferred_city",
            "preferred_education_level",
            "important_values",
            "show_photo",
            "show_city",
            "show_profession",
            "private_mode",
        ]
        widgets = {
            "short_bio": forms.Textarea(attrs={"rows": 4}),
            "important_values": forms.Textarea(attrs={"rows": 3}),
            "preferred_age_min": forms.NumberInput(attrs={"min": 18, "max": 99}),
            "preferred_age_max": forms.NumberInput(attrs={"min": 18, "max": 99}),
        }
        labels = {
            "marital_status": _("Marital status"),
            "education_level": _("Education level"),
            "profession": _("Profession"),
            "short_bio": _("Short bio"),
            "serious_intention": _("Serious intention"),
            "preferred_age_min": _("Preferred age (min)"),
            "preferred_age_max": _("Preferred age (max)"),
            "preferred_country": _("Preferred country"),
            "preferred_city": _("Preferred city"),
            "preferred_education_level": _("Preferred education level"),
            "important_values": _("Important values"),
            "show_photo": _("Show photo on profile"),
            "show_city": _("Show city on profile"),
            "show_profession": _("Show profession on profile"),
            "private_mode": _("Enable private mode"),
        }
