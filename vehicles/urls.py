"""
Fleet Manager  Vehicles URL Configuration

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



from django.urls import path
from . import views

urlpatterns = [
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.dashboard, name='dashboard'),

    path('users/',                   views.user_list,   name='user_list'),
    path('users/add/',               views.user_add,    name='user_add'),
    path('users/<int:pk>/edit/',     views.user_edit,   name='user_edit'),
    path('users/<int:pk>/delete/',   views.user_delete, name='user_delete'),

    path('vehicles/',                    views.vehicle_list,   name='vehicle_list'),
    path('vehicles/add/',                views.vehicle_add,    name='vehicle_add'),
    path('vehicles/<int:pk>/',           views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/',      views.vehicle_edit,   name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/',    views.vehicle_delete, name='vehicle_delete'),

    path('vehicles/<int:vehicle_pk>/rto/',         views.rto_add_edit, name='rto_add_edit'),
    path('vehicles/<int:vehicle_pk>/rto/doc/add/', views.rto_doc_add,  name='rto_doc_add'),
    path('rto/doc/<int:pk>/delete/',               views.rto_doc_delete, name='rto_doc_delete'),

    path('vehicles/<int:vehicle_pk>/tyre/add/', views.tyre_add,    name='tyre_add'),
    path('tyre/<int:pk>/edit/',                 views.tyre_edit,   name='tyre_edit'),
    path('tyre/<int:pk>/delete/',               views.tyre_delete, name='tyre_delete'),

    path('services/',                              views.service_list,   name='service_list'),
    path('vehicles/<int:vehicle_pk>/service/add/', views.service_add,    name='service_add'),
    path('service/<int:pk>/edit/',                 views.service_edit,   name='service_edit'),
    path('service/<int:pk>/delete/',               views.service_delete, name='service_delete'),

    path('fuel/',                              views.fuel_list,   name='fuel_list'),
    path('vehicles/<int:vehicle_pk>/fuel/add/', views.fuel_add,   name='fuel_add'),
    path('fuel/<int:pk>/edit/',                views.fuel_edit,   name='fuel_edit'),
    path('fuel/<int:pk>/delete/',              views.fuel_delete, name='fuel_delete'),

    path('reports/', views.report_view, name='reports'),
]
