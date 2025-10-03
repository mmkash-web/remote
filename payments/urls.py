"""
URL configuration for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('<uuid:payment_id>/', views.payment_detail, name='payment_detail'),
    path('manual/<uuid:customer_id>/', views.payment_manual_create, name='payment_manual_create'),
    path('<uuid:payment_id>/complete/', views.payment_mark_completed, name='payment_mark_completed'),
    path('<uuid:payment_id>/fail/', views.payment_mark_failed, name='payment_mark_failed'),
]

