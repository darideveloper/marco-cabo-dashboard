from django.contrib import admin
from travels import models


# Register your models here.
@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "last_name", "email", "phone", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "last_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.VipCode)
class VipCodeAdmin(admin.ModelAdmin):
    list_display = ("value", "active", "created_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("value", "active")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "fee", "created_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("client", "vip_code", "vehicle", "passengers", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("passengers",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.TransferType)
class TransferTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("date", "hour", "place", "type", "sale", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("date", "hour", "place", "type__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = (
        "zone",
        "location",
        "vehicle",
        "transfer_type",
        "price",
        "created_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = (
        "zone__name",
        "location__name",
        "vehicle__name",
        "transfer_type__name",
        "price",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.TransferDetail)
class TransferDetailAdmin(admin.ModelAdmin):
    list_display = (
        "client_full_name",
        "vehicle_type",
        "vehicle_fee",
        "passengers",
        "has_vip_code",
        "place",
        "hour",
        "type",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = (
        "sale__client__name",
        "sale__client__last_name",
        "sale__vehicle__name",
        "place",
        "hour",
        "type__name",
    )
    readonly_fields = ("created_at", "updated_at")

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
