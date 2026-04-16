from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Max
import os


# Create your models here.

# --------------------------Custom User model--------------------------------


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


# --------------------------- Audit mixin --------------------------------


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


# -------------------------------- Vehicle model --------------------------------


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

    vehicle_no          = models.CharField(max_length=20, unique=True)
    registration_no     = models.CharField(max_length=30, unique=True)
    chassis_no          = models.CharField(max_length=50, unique=True)
    engine_no           = models.CharField(max_length=50, unique=True)
    brand               = models.CharField(max_length=100)
    model_name          = models.CharField(max_length=100, blank=True)
    manufacture_year    = models.PositiveIntegerField()
    vehicle_type        = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default="car")
    fuel_type           = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default="petrol")
    color               = models.CharField(max_length=50, blank=True)
    current_km          = models.PositiveIntegerField(default=0)
    owner_name          = models.CharField(max_length=150, blank=True)
    notes               = models.TextField(blank=True)

    class Meta:
        ordering = ["vehicle_no"]

    def __str__(self):
        return f"{self.vehicle_no} - {self.brand} {self.model_name}"
    

    def recalculate_odometer(self):
        best = max(
            self.fuel_records.aggregate(m=Max('km_at_fill'))['m'] or 0,
            self.service_records.aggregate(m=Max('km_at_service'))['m'] or 0,
            self.tyre_records.aggregate(m=Max('km_at_change'))['m'] or 0,
        )
        if best != self.current_km:
            Vehicle.objects.filter(pk=self.pk).update(current_km=best)
            self.current_km = best


# -------------------------------- Tyre -------------------------------------


class TyreRecord(AuditMixin):
    TYRE_POSITION_CHOICES = [
        ("FL", "Front Left"),
        ("FR", "Front Right"),
        ("RL", "Rear Left"),
        ("RR", "Rear Right"),
        ("RM", "Rear Middle"),
        ("spare", "Spare"),
        ("all", "All Tyres"),
    ]

    vehicle         = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="tyre_records")
    changed_date    = models.DateField()
    km_at_change    = models.PositiveIntegerField()
    tyre_position   = models.CharField(max_length=10, choices=TYRE_POSITION_CHOICES, default="all")
    tyre_brand      = models.CharField(max_length=100, blank=True)
    tyre_size       = models.CharField(max_length=50, blank=True)
    km_used         = models.PositiveIntegerField(default=0)
    cost            = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes           = models.TextField(blank=True)

    class Meta:
        ordering = ["-changed_date", "-km_at_change"]

    def __str__(self):
        return f"{self.vehicle.vehicle_no} - Tyre @ {self.km_at_change} km"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        _sync_vehicle_odometer(self.vehicle, self.km_at_change)


# ----------------------------- Service ---------------------------------


class ServiceRecord(AuditMixin):
    vehicle                    = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="service_records")
    service_date               = models.DateField()
    km_at_service              = models.PositiveIntegerField()
    service_center             = models.CharField(max_length=200, blank=True)
    engine_oil_changed         = models.BooleanField(default=False)
    oil_filter_changed         = models.BooleanField(default=False)
    air_filter_changed         = models.BooleanField(default=False)
    fuel_filter_changed        = models.BooleanField(default=False)
    wheel_grease_applied       = models.BooleanField(default=False)
    coolant_service_done       = models.BooleanField(default=False)
    brake_fluid_changed        = models.BooleanField(default=False)
    transmission_fluid_changed = models.BooleanField(default=False)
    brake_service              = models.BooleanField(default=False)
    battery_checked            = models.BooleanField(default=False)
    ac_service                 = models.BooleanField(default=False)
    total_cost                 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_service_km            = models.PositiveIntegerField(null=True, blank=True)
    next_service_date          = models.DateField(null=True, blank=True)
    notes                      = models.TextField(blank=True)

    class Meta:
        ordering = ["-service_date", "-km_at_service"]

    def __str__(self):
        return f"{self.vehicle.vehicle_no} - Service @ {self.km_at_service} km"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        _sync_vehicle_odometer(self.vehicle, self.km_at_service)


# ----------------------------- Fuel ---------------------------------


class FuelRecord(AuditMixin):
    FUEL_STATION_TYPE = [
        ("hp", "HP"),
        ("bp", "BP"),
        ("ioc", "IOC"),
        ("essar", "Essar"),
        ("other", "Other"),
    ]

    vehicle         = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="fuel_records")
    fill_date       = models.DateField()
    km_at_fill      = models.PositiveIntegerField()
    litres_filled   = models.DecimalField(max_digits=8, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=7, decimal_places=2)
    total_amount    = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    mileage         = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, editable=False)
    fuel_station    = models.CharField(max_length=200, blank=True)
    station_type    = models.CharField(max_length=20, choices=FUEL_STATION_TYPE, default="other", blank=True)
    notes           = models.TextField(blank=True)

    class Meta:
        ordering = ["-km_at_fill", "-fill_date"]

    def __str__(self):
        return f"{self.vehicle.vehicle_no} - {self.litres_filled}L @ {self.fill_date}"

    def _compute_total_amount(self):
        if self.litres_filled and self.price_per_litre:
            return round(float(self.litres_filled) * float(self.price_per_litre), 2)
        return 0

    def _compute_mileage(self):
        if not self.km_at_fill or not self.vehicle_id:
            return None
        qs = FuelRecord.objects.filter(
            vehicle_id=self.vehicle_id, km_at_fill__lt=self.km_at_fill
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        prev = qs.order_by("-km_at_fill").first()
        if not prev or not prev.litres_filled or float(prev.litres_filled) == 0:
            return None
        distance = self.km_at_fill - prev.km_at_fill
        return round(distance / float(prev.litres_filled), 2) if distance > 0 else None

    def _refresh_next_fill_mileage(self):
        nxt = (
            FuelRecord.objects.filter(
                vehicle_id=self.vehicle_id, km_at_fill__gt=self.km_at_fill
            )
            .exclude(pk=self.pk)
            .order_by("km_at_fill")
            .first()
        )
        if nxt:
            FuelRecord.objects.filter(pk=nxt.pk).update(mileage=nxt._compute_mileage())

    def save(self, *args, **kwargs):
        self.total_amount = self._compute_total_amount()
        self.mileage = self._compute_mileage()
        super().save(*args, **kwargs)
        self._refresh_next_fill_mileage()
        _sync_vehicle_odometer(self.vehicle, self.km_at_fill)


# --------------------- RTO Document upload helper -----------------------


def rto_doc_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    name = os.path.splitext(filename)[0]
    # return f"rto_docs/vehicle_{instance.vehicle_id}/{name}{ext}"

    # Use rto_id (always set before file is saved); fall back to 'unknown'
    rto_id = instance.rto_id or (instance.rto.pk if instance.rto else "unknown")
    return f"rto_docs/rto_{rto_id}/{name}{ext}"


# --------------------- RTO Detail -------------------------------------


class RTODetail(AuditMixin):
    vehicle                  = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="rto_detail")
    rto_office               = models.CharField(max_length=200)
    rto_code                 = models.CharField(max_length=20, blank=True)
    registration_date        = models.DateField()
    registration_valid_upto  = models.DateField(null=True, blank=True)
    fitness_certificate_date = models.DateField(null=True, blank=True)
    fitness_valid_upto       = models.DateField(null=True, blank=True)
    insurance_company        = models.CharField(max_length=200, blank=True)
    insurance_policy_no      = models.CharField(max_length=100, blank=True)
    insurance_valid_upto     = models.DateField(null=True, blank=True)
    permit_no                = models.CharField(max_length=100, blank=True)
    permit_valid_upto        = models.DateField(null=True, blank=True)
    pollution_certificate_no = models.CharField(max_length=100, blank=True)
    pollution_valid_upto     = models.DateField(null=True, blank=True)
    tax_paid_upto            = models.DateField(null=True, blank=True)
    notes                    = models.TextField(blank=True)

    def __str__(self):
        return f"RTO - {self.vehicle.vehicle_no}"


# --------------------- RTO Document -------------------------------------


class RTODocument(AuditMixin):
    DOC_TYPE_CHOICES = [
        ("rc", "Registration Certificate"),
        ("insurance", "Insurance Policy"),
        ("fitness", "Fitness Certificate"),
        ("permit", "Permit"),
        ("pollution", "Pollution Certificate"),
        ("tax", "Tax Receipt"),
        ("other", "Other"),
    ]

    rto        = models.ForeignKey(RTODetail, on_delete=models.CASCADE, related_name="documents")
    doc_type   = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default="other")
    title      = models.CharField(max_length=200)
    file       = models.FileField(upload_to=rto_doc_upload_path)
    valid_upto = models.DateField(null=True, blank=True, help_text="Document validity date (optional)")
    notes      = models.TextField(blank=True)

    class Meta:
        ordering = ["doc_type", "-created_at"]

    def __str__(self):
        return f"{self.rto.vehicle.vehicle_no} – {self.title}"

    @property
    def file_extension(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower()

    @property
    def is_image(self):
        return self.file_extension in [".jpg", ".jpeg", ".png", ".gif", ".webp"]

    @property
    def is_pdf(self):
        return self.file_extension == ".pdf"

    @property
    def filename(self):
        return os.path.basename(self.file.name)


# -------------------------------- Odometer helper -----------------------------------------


def _sync_vehicle_odometer(vehicle, new_km):
    if new_km and new_km > vehicle.current_km:
        Vehicle.objects.filter(pk=vehicle.pk).update(current_km=new_km)
        vehicle.current_km = new_km
