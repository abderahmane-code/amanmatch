from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from verification.models import IdentityVerification


@admin.action(description=_("Approve selected verifications"))
def approve_verifications(modeladmin, request, queryset):
    for verification in queryset:
        verification.status = "approved"
        verification.reviewed_at = timezone.now()
        verification.save()
        account = getattr(verification.user, "account_profile", None)
        if account:
            account.is_identity_verified = True
            account.save()


@admin.action(description=_("Reject selected verifications"))
def reject_verifications(modeladmin, request, queryset):
    for verification in queryset:
        verification.status = "rejected"
        verification.reviewed_at = timezone.now()
        if not verification.rejection_reason:
            verification.rejection_reason = "Verification rejected by staff review."
        verification.save()
        account = getattr(verification.user, "account_profile", None)
        if account:
            account.is_identity_verified = False
            account.save()


@admin.register(IdentityVerification)
class IdentityVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
        "auto_result",
        "match_score",
        "submitted_at",
        "reviewed_at",
    )
    list_filter = ("status", "auto_result", "submitted_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = (
        "submitted_at",
        "reviewed_at",
        "match_score",
        "provider_response",
        "auto_result",
    )
    actions = [approve_verifications, reject_verifications]
