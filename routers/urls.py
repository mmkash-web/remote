"""
URL configuration for routers app.
"""
from django.urls import path
from . import views

app_name = 'routers'

urlpatterns = [
    path('', views.router_list, name='router_list'),
    path('create/', views.router_create, name='router_create'),
    path('<uuid:router_id>/', views.router_detail, name='router_detail'),
    path('<uuid:router_id>/edit/', views.router_edit, name='router_edit'),
    path('<uuid:router_id>/delete/', views.router_delete, name='router_delete'),
    path('<uuid:router_id>/test/', views.router_test_connection, name='router_test'),
    path('<uuid:router_id>/status/', views.router_status_ajax, name='router_status_ajax'),
    path('<uuid:router_id>/logs/', views.router_logs, name='router_logs'),
]

