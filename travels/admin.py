from django.contrib import admin
from travels import models


@admin.register(models.Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "created_at")
    list_filter = ("zone", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "last_name", "email", "phone", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "last_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.VipCode)
class VipCodeAdmin(admin.ModelAdmin):
    list_display = ("value", "active", "created_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("value",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("value",)


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "vip_code",
        "vehicle",
        "service_type",
        "passengers",
        "created_at",
    )
    list_filter = (
        "client",
        "vip_code",
        "vehicle",
        "service_type",
        "passengers",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "client__name",
        "client__email",
        "vehicle__name",
        "vip_code__value",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(models.ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("date", "hour", "location", "type", "sale", "created_at")
    list_filter = (
        "location",
        "type",
        "sale__client",
        "sale__vehicle",
        "created_at",
        "updated_at",
        "date",
    )
    search_fields = (
        "location__name",
        "type__name",
        "sale__client__name",
        "sale__client__email",
        "sale__vehicle__name",
        "sale__vip_code__value",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(models.Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = (
        "location",
        "vehicle",
        "transfer_type",
        "price",
        "created_at",
    )
    list_filter = ("location", "vehicle", "transfer_type", "created_at", "updated_at")
    search_fields = (
        "location__name",
        "vehicle__name",
        "transfer_type__name",
        "price",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("location__name", "vehicle__name", "transfer_type__name")


@admin.register(models.SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = (
        "client_full_name",
        "vehicle_type",
        "passengers",
        "has_vip_code",
        "location",
        "hour",
        "type",
    )
    list_filter = (
        "location",
        "type",
        "sale__client",
        "sale__vehicle",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "sale__client__name",
        "sale__client__last_name",
        "sale__client__email",
        "sale__vehicle__name",
        "sale__vip_code__value",
        "location__name",
        "hour",
        "type__name",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    # def client_full_name(self, obj):
    #     return obj.client_full_name

    # def vehicle_type(self, obj):
    #     return obj.vehicle_type

    # def vehicle_fee(self, obj):
    #     return obj.vehicle_fee

    # def passengers(self, obj):
    #     return obj.passengers

    # def has_vip_code(self, obj):
    #     return "Sí" if obj.has_vip_code else "No"

    # client_full_name.short_description = "Cliente"
    # vehicle_type.short_description = "Tipo de Vehículo"
    # vehicle_fee.short_description = "Tarifa"
    # has_vip_code.short_description = "¿VIP?"
