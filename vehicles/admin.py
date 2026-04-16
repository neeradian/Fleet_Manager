from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Vehicle, RTODetail, TyreRecord, ServiceRecord, FuelRecord


# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "role", "is_active"]
    list_filter = ["role", "is_active"]
    fieldsets = BaseUserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Role", {"fields": ("role",)}),)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        "vehicle_no",
        "brand",
        "model_name",
        "manufacture_year",
        "fuel_type",
        "current_km",
        "created_by",
    ]
    readonly_fields = ["created_by", "updated_by", "created_at", "updated_at"]


@admin.register(RTODetail)
class RTODetailAdmin(admin.ModelAdmin):
    list_display = [
        "vehicle",
        "rto_office",
        "registration_date",
        "insurance_valid_upto",
    ]
    readonly_fields = ["created_by", "updated_by"]


@admin.register(TyreRecord)
class TyreRecordAdmin(admin.ModelAdmin):
    list_display = [
        "vehicle",
        "changed_date",
        "km_at_change",
        "tyre_position",
        "created_by",
    ]
    readonly_fields = ["created_by", "updated_by"]


@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = [
        "vehicle",
        "service_date",
        "km_at_service",
        "total_cost",
        "created_by",
    ]
    readonly_fields = ["created_by", "updated_by"]


@admin.register(FuelRecord)
class FuelRecordAdmin(admin.ModelAdmin):
    list_display = [
        "vehicle",
        "fill_date",
        "km_at_fill",
        "litres_filled",
        "total_amount",
        "mileage",
        "created_by",
    ]
    readonly_fields = ["total_amount", "mileage", "created_by", "updated_by"]
