from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from profiles.forms import MatchmakingProfileForm
from profiles.models import MatchmakingProfile


@login_required
def profile_detail_view(request):
    profile, _created = MatchmakingProfile.objects.get_or_create(user=request.user)
    account = getattr(request.user, "account_profile", None)

    age = None
    if account and account.date_of_birth:
        today = date.today()
        dob = account.date_of_birth
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    return render(request, "profiles/detail.html", {
        "profile": profile,
        "account": account,
        "age": age,
    })


@login_required
def profile_edit_view(request):
    profile, _created = MatchmakingProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = MatchmakingProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your profile has been updated."))
            return redirect("profiles:detail")
    else:
        form = MatchmakingProfileForm(instance=profile)
    return render(request, "profiles/edit.html", {"form": form, "profile": profile})
