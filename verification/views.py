from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def verification_start_view(request):
    return render(request, "verification/start.html")
