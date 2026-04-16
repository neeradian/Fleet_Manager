import os
from datetime import timedelta, date
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import (
    VehicleForm,
    RTODetailForm,
    RTODocumentForm,
    TyreRecordForm,
    ServiceRecordForm,
    FuelRecordForm,
    LoginForm,
    UserCreateForm,
    UserEditForm,
    ReportFilterForm,
)
from .models import (
    Vehicle,
    RTODetail,
    RTODocument,
    TyreRecord,
    ServiceRecord,
    FuelRecord,
    User,
)

# Create your views here.

# ------------------ Decorators -----------------------------


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_role:
            messages.error(
                request, "You do not have permission to perform this action."
            )
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper


def save_with_audit(form, request, commit=True, vehicle=None, rto=None):
    obj = form.save(commit=False)
    if vehicle:
        obj.vehicle = vehicle
    if rto:
        obj.rto = rto
    if not obj.pk:
        obj.created_by = request.user
    obj.updated_by = request.user
    if commit:
        obj.save()
    return obj


#  ------------------------------ Authentication Views -----------------------------------------


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next", "dashboard"))
    return render(request, "vehicles/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ------------------------------ User Management Views -----------------------------------------


@admin_required
def user_list(request):
    return render(
        request,
        "vehicles/user_list.html",
        {"users": User.objects.all().order_by("username")},
    )


@admin_required
def user_add(request):
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "User created.")
        return redirect("user_list")
    return render(
        request, "vehicles/user_form.html", {"form": form, "title": "Add User"}
    )


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"User {user.username} updated.")
        return redirect("user_list")
    return render(
        request,
        "vehicles/user_form.html",
        {"form": form, "title": "Edit User", "edit_user": user},
    )


@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("user_list")
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted.")
        return redirect("user_list")
    return render(
        request, "vehicles/confirm_delete.html", {"object": user, "type": "User"}
    )


# ------------------------------ Dashboard View -----------------------------------------


@login_required
def dashboard(request):
    today = date.today()
    upcoming = today + timedelta(days=30)
    vehicles = Vehicle.objects.all()
    ctx = {
        "total_vehicles": vehicles.count(),
        "vehicles": vehicles,
        "expiring_insurance": RTODetail.objects.filter(
            insurance_valid_upto__lte=upcoming, insurance_valid_upto__gte=today
        ).select_related("vehicle"),
        "expired_insurance": RTODetail.objects.filter(
            insurance_valid_upto__lt=today
        ).select_related("vehicle"),
        "expiring_pollution": RTODetail.objects.filter(
            pollution_valid_upto__lte=upcoming, pollution_valid_upto__gte=today
        ).select_related("vehicle"),
        "recent_fuel": FuelRecord.objects.select_related(
            "vehicle", "created_by"
        ).order_by("-km_at_fill")[:10],
        "recent_service": ServiceRecord.objects.select_related(
            "vehicle", "created_by"
        ).order_by("-service_date")[:5],
        "total_fuel_cost": FuelRecord.objects.aggregate(t=Sum("total_amount"))["t"]
        or 0,
        "total_service_cost": ServiceRecord.objects.aggregate(t=Sum("total_cost"))["t"]
        or 0,
    }
    return render(request, "vehicles/dashboard.html", ctx)


# ------------------------------ Vehicle CRUD -----------------------------------------


@login_required
def vehicle_list(request):
    q = request.GET.get("q", "")
    qs = Vehicle.objects.select_related("created_by", "updated_by").all()
    if q:
        qs = qs.filter(
            Q(vehicle_no__icontains=q)
            | Q(brand__icontains=q)
            | Q(registration_no__icontains=q)
            | Q(owner_name__icontains=q)
        )
    return render(request, "vehicles/vehicle_list.html", {"vehicles": qs, "q": q})


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    try:
        rto = vehicle.rto_detail
        rto_docs = rto.documents.select_related("created_by").all()
    except RTODetail.DoesNotExist:
        rto = None
        rto_docs = []
    ctx = {
        "vehicle": vehicle,
        "rto": rto,
        "rto_docs": rto_docs,
        "tyre_records": vehicle.tyre_records.select_related(
            "created_by", "updated_by"
        ).all(),
        "service_records": vehicle.service_records.select_related(
            "created_by", "updated_by"
        ).all(),
        "fuel_records": vehicle.fuel_records.select_related(
            "created_by", "updated_by"
        ).all(),
        "total_fuel": vehicle.fuel_records.aggregate(t=Sum("total_amount"))["t"] or 0,
        "total_litres": vehicle.fuel_records.aggregate(t=Sum("litres_filled"))["t"]
        or 0,
        "total_service_cost": vehicle.service_records.aggregate(t=Sum("total_cost"))[
            "t"
        ]
        or 0,
        "today": date.today(),
    }
    return render(request, "vehicles/vehicle_detail.html", ctx)


@login_required
def vehicle_add(request):
    form = VehicleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        v = save_with_audit(form, request)
        messages.success(request, f"Vehicle {v.vehicle_no} added!")
        return redirect("vehicle_detail", pk=v.pk)
    return render(
        request, "vehicles/vehicle_form.html", {"form": form, "title": "Add Vehicle"}
    )


@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(request.POST or None, instance=vehicle)
    if request.method == "POST" and form.is_valid():
        save_with_audit(form, request)
        messages.success(request, "Vehicle updated!")
        return redirect("vehicle_detail", pk=pk)
    return render(
        request,
        "vehicles/vehicle_form.html",
        {"form": form, "title": "Edit Vehicle", "vehicle": vehicle},
    )


@admin_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        vno = vehicle.vehicle_no
        vehicle.delete()
        messages.success(request, f"Vehicle {vno} deleted.")
        return redirect("vehicle_list")
    return render(
        request, "vehicles/confirm_delete.html", {"object": vehicle, "type": "Vehicle"}
    )


# ── RTO ───────────────────────────────────────────────────────────────────────


@login_required
def rto_add_edit(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    try:
        rto = vehicle.rto_detail
    except RTODetail.DoesNotExist:
        rto = None
    form = RTODetailForm(request.POST or None, instance=rto)
    if request.method == "POST" and form.is_valid():
        save_with_audit(form, request, vehicle=vehicle)
        messages.success(request, "RTO details saved!")
        return redirect("vehicle_detail", pk=vehicle_pk)
    return render(
        request,
        "vehicles/rto_form.html",
        {"form": form, "title": "RTO Details", "vehicle": vehicle},
    )


# ---------------------------- RTO Documents --------------------------------


@login_required
def rto_doc_add(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    try:
        rto = vehicle.rto_detail
    except RTODetail.DoesNotExist:
        messages.error(request, "Please add RTO details first.")
        return redirect("rto_add_edit", vehicle_pk=vehicle_pk)
    form = RTODocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        save_with_audit(form, request, rto=rto)
        messages.success(request, "Document uploaded successfully!")
        return redirect("vehicle_detail", pk=vehicle_pk)
    return render(
        request,
        "vehicles/rto_doc_form.html",
        {"form": form, "vehicle": vehicle, "rto": rto, "title": "Upload RTO Document"},
    )


@login_required
def rto_doc_delete(request, pk):
    doc = get_object_or_404(RTODocument, pk=pk)
    vehicle_pk = doc.rto.vehicle.pk
    if request.method == "POST":
        # Delete the physical file too
        if doc.file and os.path.isfile(doc.file.path):
            os.remove(doc.file.path)
        doc.delete()
        messages.success(request, "Document deleted.")
        return redirect("vehicle_detail", pk=vehicle_pk)
    return render(
        request, "vehicles/confirm_delete.html", {"object": doc, "type": "RTO Document"}
    )


# ------------------------ Tyre Records --------------------------------


@login_required
def tyre_add(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    form = TyreRecordForm(
        request.POST or None,
        initial={"changed_date": date.today(), "km_at_change": vehicle.current_km},
    )
    if request.method == "POST" and form.is_valid():
        save_with_audit(form, request, vehicle=vehicle)
        messages.success(request, "Tyre record added!")
        return redirect("vehicle_detail", pk=vehicle_pk)
    return render(
        request,
        "vehicles/generic_form.html",
        {"form": form, "title": "Add Tyre Record", "vehicle": vehicle},
    )


@login_required
def tyre_edit(request, pk):
    tyre = get_object_or_404(TyreRecord, pk=pk)
    form = TyreRecordForm(request.POST or None, instance=tyre)
    if request.method == "POST" and form.is_valid():
        save_with_audit(form, request)
        tyre.vehicle.recalculate_odometer()
        messages.success(request, "Tyre record updated!")
        return redirect("vehicle_detail", pk=tyre.vehicle.pk)
    return render(
        request,
        "vehicles/generic_form.html",
        {"form": form, "title": "Edit Tyre Record", "vehicle": tyre.vehicle},
    )


@admin_required
def tyre_delete(request, pk):
    tyre = get_object_or_404(TyreRecord, pk=pk)
    vehicle = tyre.vehicle
    if request.method == "POST":
        tyre.delete()
        vehicle.recalculate_odometer()
        messages.success(request, "Tyre record deleted.")
        return redirect("vehicle_detail", pk=vehicle.pk)
    return render(
        request, "vehicles/confirm_delete.html", {"object": tyre, "type": "Tyre Record"}
    )


# ---------------------------- Service ---------------------------------------------


@login_required
def service_list(request):
    vf = request.GET.get("vehicle", "")
    df = request.GET.get("date_from", "")
    dt = request.GET.get("date_to", "")
    qs = ServiceRecord.objects.select_related(
        "vehicle", "created_by", "updated_by"
    ).order_by("-service_date")
    if vf:
        qs = qs.filter(vehicle__pk=vf)
    if df:
        qs = qs.filter(service_date__gte=df)
    if dt:
        qs = qs.filter(service_date__lte=dt)
    return render(
        request,
        "vehicles/service_list.html",
        {
            "records": qs,
            "vehicles": Vehicle.objects.all(),
            "vehicle_filter": vf,
            "date_from": df,
            "date_to": dt,
            "total_cost": qs.aggregate(t=Sum("total_cost"))["t"] or 0,
        },
    )


@login_required
def service_add(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    form = ServiceRecordForm(
        request.POST or None,
        initial={"service_date": date.today(), "km_at_service": vehicle.current_km},
    )
    if request.method == "POST" and form.is_valid():
        save_with_audit(form, request, vehicle=vehicle)
        messages.success(request, "Service record added!")
        return redirect("vehicle_detail", pk=vehicle_pk)
    return render(
        request,
        "vehicles/service_form.html",
        {"form": form, "title": "Add Service Record", "vehicle": vehicle},
    )


@login_required
def service_edit(request, pk):
    service = get_object_or_404(ServiceRecord, pk=pk)
    form = ServiceRecordForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        save_with_audit(form, request)
        service.vehicle.recalculate_odometer()
        messages.success(request, "Service record updated!")
        return redirect("vehicle_detail", pk=service.vehicle.pk)
    return render(
        request,
        "vehicles/service_form.html",
        {"form": form, "title": "Edit Service Record", "vehicle": service.vehicle},
    )


@admin_required
def service_delete(request, pk):
    service = get_object_or_404(ServiceRecord, pk=pk)
    vehicle = service.vehicle
    if request.method == "POST":
        service.delete()
        vehicle.recalculate_odometer()
        messages.success(request, "Service record deleted.")
        return redirect("vehicle_detail", pk=vehicle.pk)
    return render(
        request,
        "vehicles/confirm_delete.html",
        {"object": service, "type": "Service Record"},
    )


# ------------------------------ Fuel Record Forms -----------------------------------------


@login_required
def fuel_list(request):
    vf = request.GET.get("vehicle", "")
    df = request.GET.get("date_from", "")
    dt = request.GET.get("date_to", "")
    qs = FuelRecord.objects.select_related(
        "vehicle", "created_by", "updated_by"
    ).order_by("-km_at_fill")
    if vf:
        qs = qs.filter(vehicle__pk=vf)
    if df:
        qs = qs.filter(fill_date__gte=df)
    if dt:
        qs = qs.filter(fill_date__lte=dt)
    return render(
        request,
        "vehicles/fuel_list.html",
        {
            "records": qs,
            "vehicles": Vehicle.objects.all(),
            "vehicle_filter": vf,
            "date_from": df,
            "date_to": dt,
            "total": qs.aggregate(t=Sum("total_amount"))["t"] or 0,
            "total_litres": qs.aggregate(t=Sum("litres_filled"))["t"] or 0,
        },
    )


@login_required
def fuel_add(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    form = FuelRecordForm(
        request.POST or None,
        initial={"fill_date": date.today(), "km_at_fill": vehicle.current_km},
    )
    if request.method == "POST" and form.is_valid():
        obj = save_with_audit(form, request, vehicle=vehicle)
        msg = f"Fuel record added! Total: ₹{obj.total_amount}"
        if obj.mileage:
            msg += f" · Mileage: {obj.mileage} km/L"
        messages.success(request, msg)
        return redirect("vehicle_detail", pk=vehicle_pk)
    return render(
        request,
        "vehicles/fuel_form.html",
        {"form": form, "title": "Add Fuel Record", "vehicle": vehicle},
    )


@login_required
def fuel_edit(request, pk):
    fuel = get_object_or_404(FuelRecord, pk=pk)
    form = FuelRecordForm(request.POST or None, instance=fuel)
    if request.method == "POST" and form.is_valid():
        obj = save_with_audit(form, request)
        fuel.vehicle.recalculate_odometer()
        msg = f"Fuel record updated! Total: ₹{obj.total_amount}"
        if obj.mileage:
            msg += f" · Mileage: {obj.mileage} km/L"
        messages.success(request, msg)
        return redirect("vehicle_detail", pk=fuel.vehicle.pk)
    return render(
        request,
        "vehicles/fuel_form.html",
        {
            "form": form,
            "title": "Edit Fuel Record",
            "vehicle": fuel.vehicle,
            "fuel": fuel,
        },
    )


@admin_required
def fuel_delete(request, pk):
    fuel = get_object_or_404(FuelRecord, pk=pk)
    vehicle = fuel.vehicle
    if request.method == "POST":
        fuel.delete()
        vehicle.recalculate_odometer()
        nxt = (
            FuelRecord.objects.filter(vehicle=vehicle, km_at_fill__gt=fuel.km_at_fill)
            .order_by("km_at_fill")
            .first()
        )
        if nxt:
            nxt.save()
        messages.success(request, "Fuel record deleted.")
        return redirect("vehicle_detail", pk=vehicle.pk)
    return render(
        request, "vehicles/confirm_delete.html", {"object": fuel, "type": "Fuel Record"}
    )


# ------------------------------ Reports --------------------------------------


@login_required
def report_view(request):
    form = ReportFilterForm(request.GET or None)
    vehicles_qs = Vehicle.objects.all()
    vehicle_filter = request.GET.get("vehicle", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    report_type = request.GET.get("report_type", "combined")

    selected_vehicle = None
    if vehicle_filter:
        try:
            selected_vehicle = Vehicle.objects.get(pk=vehicle_filter)
        except Vehicle.DoesNotExist:
            pass

    # Build filtered querysets
    fuel_qs = FuelRecord.objects.select_related("vehicle", "created_by").order_by(
        "-km_at_fill"
    )
    service_qs = ServiceRecord.objects.select_related("vehicle", "created_by").order_by(
        "-service_date"
    )
    vehicle_list_qs = vehicles_qs

    if vehicle_filter:
        fuel_qs = fuel_qs.filter(vehicle__pk=vehicle_filter)
        service_qs = service_qs.filter(vehicle__pk=vehicle_filter)
        vehicle_list_qs = vehicle_list_qs.filter(pk=vehicle_filter)

    if date_from:
        fuel_qs = fuel_qs.filter(fill_date__gte=date_from)
        service_qs = service_qs.filter(service_date__gte=date_from)

    if date_to:
        fuel_qs = fuel_qs.filter(fill_date__lte=date_to)
        service_qs = service_qs.filter(service_date__lte=date_to)

    fuel_total = fuel_qs.aggregate(t=Sum("total_amount"))["t"] or 0
    fuel_litres = fuel_qs.aggregate(t=Sum("litres_filled"))["t"] or 0
    service_total = service_qs.aggregate(t=Sum("total_cost"))["t"] or 0

    ctx = {
        "form": form,
        "report_type": report_type,
        "vehicles": vehicles_qs,
        "vehicle_filter": vehicle_filter,
        "date_from": date_from,
        "date_to": date_to,
        "selected_vehicle": selected_vehicle,
        "fuel_records": fuel_qs if report_type in ("fuel", "combined") else [],
        "service_records": service_qs if report_type in ("service", "combined") else [],
        "vehicle_list": (
            vehicle_list_qs if report_type in ("vehicle", "combined") else []
        ),
        "fuel_total": fuel_total,
        "fuel_litres": fuel_litres,
        "service_total": service_total,
        "generated_at": date.today(),
    }

    # Print / PDF view — opens in new tab and triggers window.print()
    if "print" in request.GET:
        return render(request, "vehicles/report_print.html", ctx)

    return render(request, "vehicles/report.html", ctx)
