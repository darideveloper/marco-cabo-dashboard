from django.contrib import admin
from travels import models


# Register your models here.
@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "last_name", "email", "phone", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "last_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ("value", "active", "created_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("value", "active")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("type", "fee", "created_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("client", "code", "vehicle", "passengers", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("passengers",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("date", "hour", "place", "type", "sale", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("date", "hour", "place", "type")
    readonly_fields = ("created_at", "updated_at")