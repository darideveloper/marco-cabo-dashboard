from django.views.generic import RedirectView
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework import routers

from travels import views as travels_views


# Setup drf router
router = routers.DefaultRouter()
router.register(r"hotels", travels_views.HotelsViewSet, basename="hotels")
router.register(r"postal-codes", travels_views.PostalCodeViewSet, basename="postal-codes")
router.register(r"vehicles", travels_views.VehicleViewSet, basename="vehicles")
router.register(r"service-types", travels_views.ServiceTypeViewSet, basename="service-types")
router.register(r"pricing", travels_views.PricingViewSet, basename="pricing")


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
    # path(
    #     "api/validate-vip-code/",
    #     travels_views.VipCodeValidationView.as_view(),
    #     name="validate-vip-code",
    # ),
    path("api/sales/", travels_views.SaleViewSet.as_view(), name="sales"),
    path(
        "api/sales/done/",
        travels_views.SaleDoneView.as_view(),
        name="sale-done",
    ),
]

if not settings.STORAGE_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
