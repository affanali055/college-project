from django.urls import path
from . import views

urlpatterns = [
    path('', views.space_list_view, name='space_list'),
    path('<int:pk>/', views.space_detail_view, name='space_detail'),
    path('<int:space_id>/review/', views.submit_review_view, name='submit_review'),
]

