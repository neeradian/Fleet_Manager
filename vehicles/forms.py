from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    Vehicle,
    RTODetail,
    RTODocument,
    TyreRecord,
    ServiceRecord,
    FuelRecord,
    User,
)

# ----------------------------- Login Form ----------------------------------


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "autofocus": True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )


#  --------------- User Management Forms -------------------------------------


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role"]

    def clean_password2(self):
        p1, p2 = self.cleaned_data.get("password1"), self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "is_active"]


# ------------------------------ Vehicle Forms -----------------------------------------


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_no",
            "registration_no",
            "chassis_no",
            "engine_no",
            "brand",
            "model_name",
            "manufacture_year",
            "vehicle_type",
            "fuel_type",
            "color",
            "current_km",
            "driver_name",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "vehicle_no": forms.TextInput(attrs={"placeholder": "e.g. TN 33 AB 1234"}),
            "registration_no": forms.TextInput(
                attrs={"placeholder": "e.g. TN33AB1234"}
            ),
        }


# ------------------------------ RTO Details Forms -----------------------------------------


class RTODetailForm(forms.ModelForm):
    class Meta:
        model = RTODetail
        exclude = ["vehicle", "created_by", "updated_by"]
        widgets = {
            f: forms.DateInput(attrs={"type": "date"})
            for f in [
                "registration_date",
                "registration_valid_upto",
                "fitness_certificate_date",
                "fitness_valid_upto",
                "insurance_valid_upto",
                "permit_valid_upto",
                "pollution_valid_upto",
                "tax_paid_upto",
            ]
        }


# ------------------------------ RTO Document Forms -----------------------------------------


class RTODocumentForm(forms.ModelForm):
    class Meta:
        model = RTODocument
        exclude = ["rto", "created_by", "updated_by"]
        widgets = {
            "valid_upto": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


# ------------------------------ Tyre Record Forms -----------------------------------------


class TyreRecordForm(forms.ModelForm):
    class Meta:
        model = TyreRecord
        exclude = ["vehicle", "created_by", "updated_by"]
        widgets = {
            "changed_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


# ------------------------------ Service Record Forms -----------------------------------------


class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        exclude = ["vehicle", "created_by", "updated_by"]
        widgets = {
            "service_date": forms.DateInput(attrs={"type": "date"}),
            "next_service_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


# ------------------------------ Fuel Record Forms -----------------------------------------


class FuelRecordForm(forms.ModelForm):
    class Meta:
        model = FuelRecord
        exclude = ["vehicle", "total_amount", "mileage", "created_by", "updated_by"]
        widgets = {
            "fill_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "litres_filled": forms.NumberInput(attrs={"step": "0.01"}),
            "price_per_litre": forms.NumberInput(attrs={"step": "0.01"}),
        }


# ------------------------- Report filter form --------------------


class ReportFilterForm(forms.Form):
    REPORT_CHOICES = [
        ("vehicle", "Vehicle Report"),
        ("fuel", "Fuel Report"),
        ("service", "Service Report"),
        ("combined", "Combined (All)"),
    ]
    report_type = forms.ChoiceField(
        choices=REPORT_CHOICES, initial="combined", widget=forms.Select()
    )
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.all(),
        required=False,
        empty_label="All Vehicles",
        widget=forms.Select(),
    )
    date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
