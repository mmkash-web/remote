"""
Customer models for managing end users on MikroTik routers.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as AdminUser
import uuid

from routers.models import Router
from profiles.models import Profile


class Customer(models.Model):
    """
    Model to store customer/end-user information.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('DISABLED', 'Disabled'),
        ('PENDING', 'Pending Payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Customer information
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Router and profile assignment
    router = models.ForeignKey(Router, on_delete=models.PROTECT, related_name='customers')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='customer')
    
    # Account status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    is_active = models.BooleanField(default=False)
    
    # Dates
    created_at = models.DateTimeField(default=timezone.now)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    
    # Connection tracking
    last_connection = models.DateTimeField(null=True, blank=True)
    total_connections = models.IntegerField(default=0)
    
    # Data usage (if tracked)
    data_used_mb = models.BigIntegerField(default=0)
    
    # Financial
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    created_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, related_name='customers_created')
    notes = models.TextField(blank=True)
    
    # Flags
    auto_renewal = models.BooleanField(default=False)
    send_notifications = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['router', 'is_active']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.full_name}"
    
    def is_expired(self):
        """Check if customer account has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def days_until_expiry(self):
        """Calculate days until expiry."""
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return delta.days
        return None
    
    def get_status_badge_class(self):
        """Return CSS class for status badge."""
        status_classes = {
            'ACTIVE': 'bg-green-500',
            'EXPIRED': 'bg-red-500',
            'DISABLED': 'bg-gray-500',
            'PENDING': 'bg-yellow-500',
        }
        return status_classes.get(self.status, 'bg-gray-500')
    
    def activate(self, duration_days=None):
        """
        Activate the customer account.
        
        Args:
            duration_days: Number of days to activate for (uses profile if None)
        """
        self.is_active = True
        self.status = 'ACTIVE'
        self.activated_at = timezone.now()
        
        if duration_days:
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(days=duration_days)
        else:
            self.expires_at = self.profile.calculate_expiry_date()
        
        self.save()
    
    def extend_subscription(self, additional_days=None):
        """
        Extend customer subscription.
        
        Args:
            additional_days: Days to add (uses profile duration if None)
        """
        if additional_days is None:
            # Use profile duration
            additional_days = self.profile.duration_value
            if self.profile.duration_unit == 'MONTHS':
                additional_days *= 30
            elif self.profile.duration_unit == 'WEEKS':
                additional_days *= 7
            elif self.profile.duration_unit == 'HOURS':
                additional_days = additional_days / 24
        
        from datetime import timedelta
        if self.expires_at and self.expires_at > timezone.now():
            # Extend from current expiry
            self.expires_at += timedelta(days=additional_days)
        else:
            # Start from now
            self.expires_at = timezone.now() + timedelta(days=additional_days)
        
        self.is_active = True
        self.status = 'ACTIVE'
        self.save()
    
    def disable(self):
        """Disable the customer account."""
        self.is_active = False
        self.status = 'DISABLED'
        self.save()


class CustomerSession(models.Model):
    """
    Track customer connection sessions.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sessions')
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    caller_id = models.CharField(max_length=100, blank=True)
    
    # Data usage
    bytes_in = models.BigIntegerField(default=0)
    bytes_out = models.BigIntegerField(default=0)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Customer Session'
        verbose_name_plural = 'Customer Sessions'
        indexes = [
            models.Index(fields=['customer', '-started_at']),
            models.Index(fields=['-started_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} - {self.started_at}"
    
    def is_active(self):
        """Check if session is currently active."""
        return self.ended_at is None
    
    def get_duration_display(self):
        """Get human-readable duration."""
        if self.duration_seconds:
            hours = self.duration_seconds // 3600
            minutes = (self.duration_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0h 0m"
    
    def get_data_usage_display(self):
        """Get human-readable data usage."""
        total_mb = (self.bytes_in + self.bytes_out) / (1024 * 1024)
        if total_mb > 1024:
            return f"{total_mb / 1024:.2f} GB"
        return f"{total_mb:.2f} MB"

