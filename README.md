
# 🚛 FleetTrack Pro — Django Vehicle Management System

A full-featured Django web application for managing your vehicle fleet including service records, tyre changes, fuel logs, and RTO compliance with role-based auth, document uploads, filtered reports, and clean static CSS/JS architecture.

---

## 🚀 Quick Setup

### 1. Create a Virtual Environment

```bash
# Using venv
python -m venv venv
```

### 2. Activate virtual environment

####  On Windows:
```bash
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
source venv/bin/activate
```

#### If activation fails, run:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```


### 3. Clone the repository
```bash
git clone https://github.com/neeradian/Fleet_Manager.git
```


### 4. Install Dependencies

```bash
cd fleet_manager
pip install -r requirements.txt
```


### 5. Copy the commands
```bash
python manage.py migrate
python manage.py create_admin
python manage.py runserver
```

Open `http://127.0.0.1:8000/` → login page.

---

## 👤 Demo Accounts

| Username | Password | Role   |
|----------|----------|--------|
| admin    | admin123 | Admin  |
| staff    | staff123 | Staff  |

---



## 🔐 Role Permissions

| Feature              | Admin | Staff |
|----------------------|-------|-------|
| View all records     | ✅    | ✅    |
| Add / Edit records   | ✅    | ✅    |
| Upload RTO documents | ✅    | ✅    |
| Delete records       | ✅    | ❌    |
| Delete documents     | ✅    | ❌    |
| User management      | ✅    | ❌    |
| Add vehicles         | ✅    | ❌    |
| Download reports     | ✅    | ✅    |

---

## 📁 Project Structure

```
fleet_manager/
├── manage.py
├── requirements.txt          # Django>=4.2, Pillow>=10
├── media/                    # Uploaded documents (auto-created)
│   └── rto_docs/
├── static/
│   ├── css/fleet.css         # All styles
│   └── js/fleet.js           # Fuel preview, drag-drop upload, report toggles
├── fleet_manager/
│   ├── settings.py           # AUTH_USER_MODEL, MEDIA_ROOT, LOGIN_URL
│   └── urls.py               # Includes media serving in DEBUG
└── vehicles/
    ├── models.py             # User, Vehicle, RTODetail, RTODocument,
    │                         #   TyreRecord, ServiceRecord, FuelRecord
    ├── views.py              # All views + report_view + rto_doc_add/delete
    ├── forms.py              # RTODocumentForm, ReportFilterForm + all others
    ├── urls.py               # All routes including /reports/, /rto/doc/
    ├── admin.py
    ├── migrations/
    │   └── 0001_initial.py
    │    
    ├── management/commands/create_admin.py
    └── templates/vehicles/
        ├── base.html              # Loads fleet.css + fleet.js
        ├── login.html             # Standalone (own styles)
        ├── dashboard.html
        ├── vehicle_list.html / vehicle_detail.html / vehicle_form.html
        ├── rto_form.html          # RTO details form
        ├── rto_doc_form.html      # Document upload with drag-and-drop
        ├── service_list.html / service_form.html
        ├── fuel_list.html / fuel_form.html
        ├── generic_form.html      # Tyre records
        ├── report.html            # Interactive report page
        ├── report_print.html      # Self-contained downloadable HTML
        ├── user_list.html / user_form.html
        └── confirm_delete.html
```


---

## ✨ Features

### 🚗 Vehicle Management
- Add/Edit/Delete vehicles
- Vehicle Number, Registration No., Chassis No., Engine No.
- Brand, Model, Manufacture Year, Fuel Type, Vehicle Type
- Current odometer tracking

### 📋 RTO Details (per vehicle)
- RTO Office & Code
- Registration date & validity
- Fitness certificate
- Insurance details + expiry alerts
- Permit details
- Pollution certificate
- Tax paid date

### 🔄 Tyre Records
- Date & odometer at tyre change
- Tyre position (FL/FR/RL/RR/Spare/All)
- Tyre brand & size
- KM used before change
- Cost tracking

### 🔧 Service Records
- Service date & odometer
- Service center
- Checkboxes for: Engine Oil, Oil Filter, Air Filter, Fuel Filter
- Wheel Grease Applied
- Coolant Service Done
- Brake Fluid, Transmission Fluid, Brake Service
- Battery Check, AC Service
- Next service due KM & date

### ⛽ Fuel Records
- Date, odometer at fill
- Litres filled, price per litre, total amount
- Fuel station name & type (HP/BP/IOC/etc.)
- Mileage (km/L) tracking

### 📊 Dashboard
- Fleet overview with stats
- Insurance expiry alerts (30-day warning)
- Pollution certificate alerts
- Recent fuel & service activity
- Total cost tracking


### 🧮 Auto-Calculations (FuelRecord)
- `total_amount` = litres_filled × price_per_litre (auto on save)
- `mileage` = distance from prev fill ÷ prev fill litres (auto on save)
- Displayed as plain number (e.g. `18.5 km/L`)


### 📍 Auto Odometer Sync
- `vehicle.current_km` auto-updates to the highest odometer reading across all fuel, service, and tyre records


### 📋 Audit Trail
- Every record tracks: `created_by`, `updated_by`, `created_at`, `updated_at`
- Visible in detail views, list views, and Django admin


### 📊 Separate List Pages
- `/services/` — all service records across fleet, filterable by vehicle
- `/fuel/` — all fuel records across fleet, filterable by vehicle


---

