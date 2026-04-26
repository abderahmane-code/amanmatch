from django.urls import path

from verification.views import verification_start_view

app_name = "verification"

urlpatterns = [
    path("start/", verification_start_view, name="start"),
]
