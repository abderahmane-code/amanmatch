from django.contrib import admin

from profiles.models import MatchmakingProfile


@admin.register(MatchmakingProfile)
class MatchmakingProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "marital_status",
        "education_level",
        "profession",
        "serious_intention",
        "private_mode",
    )
    list_filter = ("marital_status", "serious_intention", "private_mode")
    search_fields = ("user__username", "user__email", "profession", "education_level")
    readonly_fields = ("created_at", "updated_at")
