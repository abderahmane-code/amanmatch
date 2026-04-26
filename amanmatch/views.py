from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def landing_view(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html")
    return render(request, "landing.html")


@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")
