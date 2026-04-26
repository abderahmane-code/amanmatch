from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Welcome to AmanMatch! Your account has been created."))
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})
