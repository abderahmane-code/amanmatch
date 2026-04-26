from django.urls import path

from verification.views import verification_start_view, verification_status_view

app_name = "verification"

urlpatterns = [
    path("start/", verification_start_view, name="start"),
    path("status/", verification_status_view, name="status"),
]
