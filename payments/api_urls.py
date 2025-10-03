"""
API URL configuration for payment callbacks and integrations.
"""
from django.urls import path
from . import api_views

app_name = 'payments_api'

urlpatterns = [
    # Payment callback endpoints (for M-Pesa, PayPal, etc.)
    path('payment/callback/', api_views.payment_callback, name='payment_callback'),
    path('payment/mpesa/callback/', api_views.mpesa_callback, name='mpesa_callback'),
    path('payment/paypal/callback/', api_views.paypal_callback, name='paypal_callback'),
    
    # Customer payment initiation (for customer self-service portal)
    path('payment/initiate/', api_views.initiate_payment, name='initiate_payment'),
]

