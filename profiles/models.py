"""
Profile models for managing bandwidth and pricing plans.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import uuid


class Profile(models.Model):
    """
    Model to store bandwidth profiles with pricing and duration.
    """
    DURATION_UNITS = [
        ('HOURS', 'Hours'),
        ('DAYS', 'Days'),
        ('WEEKS', 'Weeks'),
        ('MONTHS', 'Months'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Bandwidth settings
    download_speed = models.CharField(
        max_length=20,
        help_text="Download speed limit (e.g., 5M, 10M, 100M)"
    )
    upload_speed = models.CharField(
        max_length=20,
        help_text="Upload speed limit (e.g., 5M, 10M, 100M)"
    )
    rate_limit = models.CharField(
        max_length=50,
        blank=True,
        help_text="Combined rate limit (e.g., 5M/5M). Auto-generated if empty."
    )
    
    # Data limits (optional)
    data_limit_mb = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total data limit in MB (leave empty for unlimited)"
    )
    
    # Duration and pricing
    duration_value = models.IntegerField(help_text="Duration value (e.g., 1, 7, 30)")
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNITS, default='DAYS')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in your currency (e.g., KES, USD)"
    )
    currency = models.CharField(max_length=3, default='KES')
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(
        default=True,
        help_text="Show this profile to customers on self-service portal"
    )
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='profiles_created')
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_customers = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['price']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        indexes = [
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_speed_display()} - {self.currency} {self.price}"
    
    def save(self, *args, **kwargs):
        """Auto-generate rate_limit if not provided."""
        if not self.rate_limit:
            self.rate_limit = f"{self.upload_speed}/{self.download_speed}"
        super().save(*args, **kwargs)
    
    def get_speed_display(self):
        """Get human-readable speed display."""
        return f"{self.download_speed}↓ / {self.upload_speed}↑"
    
    def get_duration_display_text(self):
        """Get human-readable duration."""
        unit = self.duration_unit.lower()
        if self.duration_value == 1:
            unit = unit.rstrip('s')  # Remove 's' for singular
        return f"{self.duration_value} {unit}"
    
    def calculate_expiry_date(self, start_date=None):
        """
        Calculate expiry date based on duration.
        
        Args:
            start_date: Starting date (defaults to now)
        
        Returns:
            datetime: Expiry date
        """
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        if start_date is None:
            start_date = timezone.now()
        
        if self.duration_unit == 'HOURS':
            return start_date + timedelta(hours=self.duration_value)
        elif self.duration_unit == 'DAYS':
            return start_date + timedelta(days=self.duration_value)
        elif self.duration_unit == 'WEEKS':
            return start_date + timedelta(weeks=self.duration_value)
        elif self.duration_unit == 'MONTHS':
            return start_date + relativedelta(months=self.duration_value)
        
        return start_date
    
    def get_mikrotik_profile_name(self):
        """Get the profile name to use in MikroTik."""
        # Sanitize name for MikroTik (no special characters)
        return self.name.replace(' ', '_').replace('-', '_')

