from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from accounts.forms import AmanMatchRegistrationForm
from accounts.models import AccountProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = AmanMatchRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save()
            AccountProfile.objects.create(
                user=user,
                gender=form.cleaned_data["gender"],
                date_of_birth=form.cleaned_data["date_of_birth"],
                country=form.cleaned_data["country"],
                city=form.cleaned_data["city"],
                phone_number=form.cleaned_data.get("phone_number", ""),
            )
            login(request, user)
            messages.success(request, _("Welcome to AmanMatch! Your account has been created."))
            return redirect("dashboard")
    else:
        form = AmanMatchRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})
