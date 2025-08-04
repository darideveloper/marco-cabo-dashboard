from django.views.generic import RedirectView
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework import routers

from travels.views import VehicleViewSet


# Setup drf router
router = routers.DefaultRouter()
router.register(r"vehicles", VehicleViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    # >Redirects
    path("", RedirectView.as_view(url="/admin/"), name="home-redirect-admin"),
    path(
        "accounts/login/",
        RedirectView.as_view(url="/admin/"),
        name="login-redirect-admin",
    ),
    
    # API URLs
    path("api/", include(router.urls)),
]

if not settings.STORAGE_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
