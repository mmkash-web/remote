"""
Voucher models for prepaid access codes.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as AdminUser
import uuid
import random
import string

from routers.models import Router
from profiles.models import Profile
from customers.models import Customer


class VoucherBatch(models.Model):
    """
    Batch of vouchers generated together.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    router = models.ForeignKey(Router, on_delete=models.PROTECT)
    
    quantity = models.IntegerField()
    price_per_voucher = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Voucher Batch'
        verbose_name_plural = 'Voucher Batches'
    
    def __str__(self):
        return f"{self.name} - {self.quantity} vouchers"
    
    def get_used_count(self):
        """Get number of used vouchers in this batch."""
        return self.vouchers.filter(is_used=True).count()
    
    def get_available_count(self):
        """Get number of available vouchers in this batch."""
        return self.vouchers.filter(is_used=False, is_active=True).count()


class Voucher(models.Model):
    """
    Individual voucher/access code.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    
    batch = models.ForeignKey(VoucherBatch, on_delete=models.CASCADE, related_name='vouchers')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    router = models.ForeignKey(Router, on_delete=models.PROTECT)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    
    # Usage tracking
    used_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    used_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Dates
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_used', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {'Used' if self.is_used else 'Available'}"
    
    @staticmethod
    def generate_code(length=12):
        """Generate a random voucher code."""
        chars = string.ascii_uppercase + string.digits
        # Exclude confusing characters
        chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
        
        code = ''.join(random.choice(chars) for _ in range(length))
        
        # Format as XXXX-XXXX-XXXX
        if length == 12:
            code = f"{code[:4]}-{code[4:8]}-{code[8:12]}"
        
        return code
    
    def mark_as_used(self, customer, ip_address=None):
        """Mark voucher as used by a customer."""
        self.is_used = True
        self.used_by = customer
        self.used_at = timezone.now()
        self.used_ip = ip_address
        self.save()
    
    def is_valid(self):
        """Check if voucher is valid (active, not used, not expired)."""
        if not self.is_active or self.is_used:
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            return False
        
        return True

