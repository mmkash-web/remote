"""
Router models for managing MikroTik routers.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import uuid


class Router(models.Model):
    """
    Model to store MikroTik router information and credentials.
    """
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('ERROR', 'Error'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Connection details
    vpn_ip = models.GenericIPAddressField(help_text="VPN tunnel IP (e.g., 10.10.0.2)")
    api_port = models.IntegerField(
        default=8728,
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255, help_text="Router admin password")
    
    # Status and health
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNKNOWN')
    last_checked = models.DateTimeField(null=True, blank=True)
    last_online = models.DateTimeField(null=True, blank=True)
    
    # Router information (fetched from API)
    router_model = models.CharField(max_length=100, blank=True)
    router_version = models.CharField(max_length=50, blank=True)
    router_identity = models.CharField(max_length=100, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='routers_created')
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Router'
        verbose_name_plural = 'Routers'
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['vpn_ip']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.vpn_ip})"
    
    def is_online(self):
        """Check if router is online."""
        return self.status == 'ONLINE'
    
    def get_status_badge_class(self):
        """Return Bootstrap/Tailwind class for status badge."""
        status_classes = {
            'ONLINE': 'bg-green-500',
            'OFFLINE': 'bg-red-500',
            'ERROR': 'bg-yellow-500',
            'UNKNOWN': 'bg-gray-500',
        }
        return status_classes.get(self.status, 'bg-gray-500')
    
    def update_status(self, status, save=True):
        """Update router status and timestamp."""
        self.status = status
        self.last_checked = timezone.now()
        if status == 'ONLINE':
            self.last_online = timezone.now()
        if save:
            self.save(update_fields=['status', 'last_checked', 'last_online'])


class RouterLog(models.Model):
    """
    Log all API interactions with routers.
    """
    LOG_TYPES = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('SUCCESS', 'Success'),
    ]
    
    router = models.ForeignKey(Router, on_delete=models.CASCADE, related_name='logs')
    log_type = models.CharField(max_length=10, choices=LOG_TYPES)
    action = models.CharField(max_length=100)
    message = models.TextField()
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Router Log'
        verbose_name_plural = 'Router Logs'
        indexes = [
            models.Index(fields=['router', '-created_at']),
            models.Index(fields=['log_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.router.name} - {self.action} ({self.created_at})"

