from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from vehicles.models import User, Vehicle


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
