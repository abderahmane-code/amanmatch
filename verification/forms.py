from django import forms
from django.utils.translation import gettext_lazy as _

from verification.models import IdentityVerification


class IdentityVerificationForm(forms.ModelForm):
    confirmation = forms.BooleanField(
        required=True,
        label=_(
            "I confirm that I am submitting my own identity document "
            "and my own real selfie."
        ),
    )

    class Meta:
        model = IdentityVerification
        fields = ["document_image", "selfie_image"]
        labels = {
            "document_image": _("Identity document image"),
            "selfie_image": _("Selfie image"),
        }
        help_texts = {
            "document_image": _("Upload a clear photo of your government-issued ID."),
            "selfie_image": _("Take a clear selfie of your face."),
        }
