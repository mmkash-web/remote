"""
URL configuration for reports app.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('revenue/', views.revenue_report, name='revenue'),
    path('customers/', views.customer_report, name='customers'),
    path('routers/', views.router_report, name='routers'),
    path('saved/', views.saved_reports_list, name='saved_list'),
    path('saved/<uuid:report_id>/', views.saved_report_detail, name='saved_detail'),
]

