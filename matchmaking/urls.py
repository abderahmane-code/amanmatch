from django.urls import path

from matchmaking import views

app_name = "matchmaking"

urlpatterns = [
    path("search/", views.search_view, name="search"),
    path("profile/<int:user_id>/", views.public_profile_view, name="public_profile"),
    path("interest/send/<int:user_id>/", views.send_interest_view, name="send_interest"),
    path("interest/accept/<int:interest_id>/", views.accept_interest_view, name="accept_interest"),
    path("interest/reject/<int:interest_id>/", views.reject_interest_view, name="reject_interest"),
    path("interests/received/", views.received_interests_view, name="received_interests"),
    path("interests/sent/", views.sent_interests_view, name="sent_interests"),
    path("matches/", views.matches_view, name="matches"),
]
