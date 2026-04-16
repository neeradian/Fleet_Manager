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

    
]
