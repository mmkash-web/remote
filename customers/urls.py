"""
URL configuration for customers app.
"""
from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<uuid:customer_id>/', views.customer_detail, name='customer_detail'),
    path('<uuid:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('<uuid:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    path('<uuid:customer_id>/enable/', views.customer_enable, name='customer_enable'),
    path('<uuid:customer_id>/disable/', views.customer_disable, name='customer_disable'),
    path('<uuid:customer_id>/extend/', views.customer_extend, name='customer_extend'),
    path('<uuid:customer_id>/sessions/', views.customer_sessions, name='customer_sessions'),
    path('active-sessions/', views.active_sessions_view, name='active_sessions'),
]

