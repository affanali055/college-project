from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.create_booking_view, name='create_booking'),
    path('update-status/<int:pk>/<str:status>/', views.update_booking_status_view, name='update_booking_status'),
    path('cancel/<int:pk>/', views.cancel_booking_view, name='cancel_booking'),
    path('inquire/<int:space_id>/', views.create_inquiry_view, name='create_inquiry'),
]
