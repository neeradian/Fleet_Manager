from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

# -------------------------------------Custom User model-----------------------------------------


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_STAFF = "staff"
    ROLE_CHOICES = [(ROLE_ADMIN, "Admin"), (ROLE_STAFF, "Staff")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STAFF)

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# ------------------------------------ Audit mixin ----------------------------------------------


class AuditMixin(models.Model):
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        editable=False,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ------------------------------------ Vehicle model ----------------------------------------------


class Vehicle(AuditMixin):
    FUEL_TYPE_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("cng", "CNG"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
    ]
    VEHICLE_TYPE_CHOICES = [
        ("car", "Car"),
        ("truck", "Truck"),
        ("bus", "Bus"),
        ("motorcycle", "Motorcycle"),
        ("van", "Van"),
        ("tempo", "Tempo"),
        ("tractor", "Tractor"),
        ("other", "Other"),
    ]
    vehicle_no = models.CharField(max_length=20, unique=True)
    registration_no = models.CharField(max_length=30, unique=True)
    chassis_no = models.CharField(max_length=50, unique=True)
    engine_no = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, blank=True)
    manufacture_year = models.PositiveIntegerField()
    vehicle_type = models.CharField(
        max_length=20, choices=VEHICLE_TYPE_CHOICES, default="car"
    )
    fuel_type = models.CharField(
        max_length=20, choices=FUEL_TYPE_CHOICES, default="petrol"
    )
    color = models.CharField(max_length=50, blank=True)
    current_km = models.PositiveIntegerField(default=0)
    owner_name = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["vehicle_no"]

    def __str__(self):
        return f"{self.vehicle_no} - {self.brand} {self.model_name}"
