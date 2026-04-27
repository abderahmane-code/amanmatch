from django.urls import path

from matchmaking import views

app_name = "matchmaking"

urlpatterns = [
    path("search/", views.search_view, name="search"),
    path("profile/<int:user_id>/", views.public_profile_view, name="public_profile"),
]
