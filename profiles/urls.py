"""
URL configuration for profiles app.
"""
from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_list, name='profile_list'),
    path('create/', views.profile_create, name='profile_create'),
    path('<uuid:profile_id>/', views.profile_detail, name='profile_detail'),
    path('<uuid:profile_id>/edit/', views.profile_edit, name='profile_edit'),
    path('<uuid:profile_id>/delete/', views.profile_delete, name='profile_delete'),
]

