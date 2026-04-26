from django.contrib import admin

from accounts.models import AccountProfile


@admin.register(AccountProfile)
class AccountProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "country", "city", "is_identity_verified", "created_at")
    list_filter = ("gender", "country", "is_identity_verified")
    search_fields = ("user__username", "user__email", "country", "city")
    readonly_fields = ("created_at", "updated_at")
