from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from profiles.models import MatchmakingProfile
from verification.models import IdentityVerification


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

    latest_verification = (
        IdentityVerification.objects.filter(user=request.user)
        .order_by("-submitted_at")
        .first()
    )
    verification_status = latest_verification.status if latest_verification else None

    return {
        "profile_completion": completion,
        "verification_status": verification_status,
    }
