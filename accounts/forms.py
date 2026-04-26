from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from accounts.models import AccountProfile


class AmanMatchRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label=_("First name"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Last name"))
    email = forms.EmailField(required=True, label=_("Email"))
    gender = forms.ChoiceField(choices=AccountProfile.GENDER_CHOICES, label=_("Gender"))
    date_of_birth = forms.DateField(
        label=_("Date of birth"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    country = forms.CharField(max_length=100, label=_("Country"))
    city = forms.CharField(max_length=100, label=_("City"))
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label=_("Phone number"),
        help_text=_("Optional. Include country code."),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_date_of_birth(self):
        dob = self.cleaned_data["date_of_birth"]
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise forms.ValidationError(
                _("You must be at least 18 years old to use AmanMatch.")
            )
        return dob
