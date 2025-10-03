"""
URL configuration for vouchers app.
"""
from django.urls import path
from . import views

app_name = 'vouchers'

urlpatterns = [
    path('batches/', views.voucher_batch_list, name='batch_list'),
    path('batches/create/', views.voucher_batch_create, name='batch_create'),
    path('batches/<uuid:batch_id>/', views.voucher_batch_detail, name='batch_detail'),
    path('batches/<uuid:batch_id>/export/', views.voucher_batch_export, name='batch_export'),
    path('', views.voucher_list, name='voucher_list'),
    path('redeem/', views.voucher_redeem, name='redeem'),
]

