from django.contrib import admin
from django.utils.html import format_html

from travels import models


@admin.register(models.Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "updated_at")
    list_filter = ("zone", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "last_name", "email", "phone", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "last_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.VipCode)
class VipCodeAdmin(admin.ModelAdmin):
    list_display = ("value", "active", "updated_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("value",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("value",)


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "passengers", "updated_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "stripe_code",
        "client",
        # "vip_code",
        "vehicle",
        "service_type",
        "location",
        "passengers",
        "total",
        "paid",
        "custom_links",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "client",
        # "vip_code",
        "vehicle",
        "service_type",
        "location",
        "passengers",
        "paid",
        "created_at",
    )
    search_fields = (
        "client__name",
        "client__email",
        "vehicle__name",
        # "vip_code__value",
        "total",
    )
    readonly_fields = ("stripe_code", "created_at", "updated_at")
    ordering = ("-created_at",)
    
    # CUSTOM FIELDS
    def custom_links(self, obj):
        """Create custom Imprimir and Ver buttons"""
        return format_html(
            '<a class="btn btn-secondary my-1" href="{}">Transportaciones</a>',
            f"/admin/travels/transfer/?sale__id__exact={obj.id}&q=",
        )

    # Labels for custom fields
    custom_links.short_description = "Acciones"


@admin.register(models.ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "updated_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("date", "hour", "type", "sale", "updated_at")
    list_filter = (
        "type",
        "sale",
        "sale__client",
        "sale__vehicle",
        "sale__location",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "sale__location__name",
        "sale__client__name",
        "sale__client__email",
        "sale__vehicle__name",
        # "sale__vip_code__value",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(models.Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = (
        "location",
        "vehicle",
        "service_type",
        "price",
        "updated_at",
    )
    list_filter = ("location", "vehicle", "service_type", "created_at", "updated_at")
    search_fields = (
        "location__name",
        "vehicle__name",
        "service_type__name",
        "price",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("location__name", "vehicle__name", "service_type__name")