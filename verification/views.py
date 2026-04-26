from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from verification.forms import IdentityVerificationForm
from verification.models import IdentityVerification
from verification.services.face_matcher import compare_document_and_selfie


@login_required
def verification_start_view(request):
    pending = IdentityVerification.objects.filter(
        user=request.user, status="pending"
    ).exists()
    if pending:
        messages.info(request, _("You already have a pending verification request."))
        return redirect("verification:status")

    if request.method == "POST":
        form = IdentityVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.user = request.user
            verification.save()

            result = compare_document_and_selfie(
                verification.document_image.path,
                verification.selfie_image.path,
            )
            verification.match_score = result["match_score"]
            verification.provider_response = result
            if result["match_score"] >= 0.80:
                verification.auto_result = "possible_match"
            else:
                verification.auto_result = "possible_mismatch"
            verification.save()

            messages.success(
                request,
                _("Verification submitted. Your request is pending review."),
            )
            return redirect("verification:status")
    else:
        form = IdentityVerificationForm()

    return render(request, "verification/start.html", {"form": form})


@login_required
def verification_status_view(request):
    latest = (
        IdentityVerification.objects.filter(user=request.user)
        .order_by("-submitted_at")
        .first()
    )
    return render(request, "verification/status.html", {"verification": latest})
