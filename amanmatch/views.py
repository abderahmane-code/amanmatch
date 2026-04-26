from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from profiles.models import MatchmakingProfile


def landing_view(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html", _dashboard_context(request))
    return render(request, "landing.html")


@login_required
def dashboard_view(request):
    return render(request, "dashboard.html", _dashboard_context(request))


def _dashboard_context(request):
    profile = getattr(request.user, "matchmaking_profile", None)
    completion = profile.completion_percentage if profile else 0
    return {"profile_completion": completion}
