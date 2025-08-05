from django.views.generic import RedirectView
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework import routers

from travels import views as travels_views


# Setup drf router
router = routers.DefaultRouter()
router.register(r"zones", travels_views.ZoneViewSet)
router.register(r"locations", travels_views.LocationViewSet)
router.register(r"vehicles", travels_views.VehicleViewSet)


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
