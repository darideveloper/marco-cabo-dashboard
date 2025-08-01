from django.views.generic import RedirectView
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/"), name="home-redirect-admin"),
    path("admin/", admin.site.urls),
]

if not settings.STORAGE_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
