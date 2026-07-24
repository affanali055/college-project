from django.urls import path
from . import views

urlpatterns = [
    path('', views.space_list_view, name='space_list'),
    path('<int:pk>/', views.space_detail_view, name='space_detail'),
]
