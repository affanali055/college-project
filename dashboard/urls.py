from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_home_view, name='landing_home'),
    path('dashboard/', views.dashboard_home_view, name='dashboard_home'),
    path('dashboard/client/', views.dashboard_client_view, name='dashboard_client'),
    path('dashboard/owner/', views.dashboard_owner_view, name='dashboard_owner'),
    path('dashboard/admin/', views.dashboard_admin_view, name='dashboard_admin'),
]
