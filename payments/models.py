"""
Payment models for tracking customer payments.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as AdminUser
from decimal import Decimal
import uuid

from customers.models import Customer
from profiles.models import Profile


class Payment(models.Model):
    """
    Model to track all payment transactions.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('MPESA', 'M-Pesa'),
        ('PAYPAL', 'PayPal'),
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('VOUCHER', 'Voucher'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Customer and profile
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='payments')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Transaction reference
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    reference_code = models.CharField(max_length=100, blank=True)
    
    # Gateway response
    gateway_response = models.JSONField(null=True, blank=True)
    
    # Dates
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Processing
    processed_by = models.ForeignKey(
        AdminUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_processed'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} - {self.currency} {self.amount} - {self.status}"
    
    def mark_completed(self, transaction_id=None):
        """Mark payment as completed and activate/extend customer."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        
        if transaction_id:
            self.transaction_id = transaction_id
        
        self.save()
        
        # Update customer
        if self.customer.is_active and self.customer.expires_at > timezone.now():
            # Extend existing subscription
            self.customer.extend_subscription()
        else:
            # Activate new subscription
            self.customer.activate()
        
        # Update customer's payment info
        self.customer.last_payment_date = timezone.now()
        self.customer.total_paid += self.amount
        self.customer.save()
        
        # Enable on router if disabled
        from routers.services.mikrotik_api import MikroTikAPIService
        api_service = MikroTikAPIService(self.customer.router)
        api_service.enable_ppp_secret(self.customer.username)
    
    def mark_failed(self, reason=''):
        """Mark payment as failed."""
        self.status = 'FAILED'
        if reason:
            self.notes = reason
        self.save()
    
    def get_status_badge_class(self):
        """Return CSS class for status badge."""
        status_classes = {
            'PENDING': 'bg-yellow-500',
            'COMPLETED': 'bg-green-500',
            'FAILED': 'bg-red-500',
            'REFUNDED': 'bg-blue-500',
            'CANCELLED': 'bg-gray-500',
        }
        return status_classes.get(self.status, 'bg-gray-500')


class PaymentGatewayLog(models.Model):
    """
    Log all payment gateway API interactions.
    """
    LOG_TYPES = [
        ('REQUEST', 'Request'),
        ('RESPONSE', 'Response'),
        ('CALLBACK', 'Callback'),
        ('ERROR', 'Error'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='gateway_logs', null=True, blank=True)
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    gateway = models.CharField(max_length=50)
    
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    
    status_code = models.IntegerField(null=True, blank=True)
    message = models.TextField()
    
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Gateway Log'
        verbose_name_plural = 'Payment Gateway Logs'
        indexes = [
            models.Index(fields=['payment', '-created_at']),
            models.Index(fields=['log_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.gateway} - {self.log_type} - {self.created_at}"

