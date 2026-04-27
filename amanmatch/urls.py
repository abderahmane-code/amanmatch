from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from amanmatch.views import dashboard_view, landing_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing_view, name="landing"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("accounts/", include("accounts.urls")),
    path("verification/", include("verification.urls")),
    path("profiles/", include("profiles.urls")),
    path("matchmaking/", include("matchmaking.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
