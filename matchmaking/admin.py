from django.contrib import admin

from matchmaking.models import Interest, Match


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "status", "created_at")
    list_filter = ("status", "created_at")
    raw_id_fields = ("sender", "receiver")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("user1", "user2", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    raw_id_fields = ("user1", "user2")
