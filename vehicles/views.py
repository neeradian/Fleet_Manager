import os
from datetime import timedelta, date
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404, redirect

from vehicles.forms import LoginForm

from .models import (
    User,
    Vehicle,
)

# Create your views here.


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

"""
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

"""
    
# ------------------------------ Dashboard View -----------------------------------------
"""
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
"""
