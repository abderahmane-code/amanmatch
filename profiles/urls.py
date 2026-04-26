from django.urls import path

from profiles.views import profile_detail_view, profile_edit_view

app_name = "profiles"

urlpatterns = [
    path("me/", profile_detail_view, name="detail"),
    path("edit/", profile_edit_view, name="edit"),
]
