"""
Reports models for storing generated reports.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class Report(models.Model):
    """
    Model to store generated reports.
    """
    REPORT_TYPES = [
        ('DAILY', 'Daily Report'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report'),
        ('REVENUE', 'Revenue Report'),
        ('CUSTOMERS', 'Customers Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    
    # Date range
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Report data
    data = models.JSONField()
    summary = models.TextField(blank=True)
    
    # Generation info
    generated_at = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        indexes = [
            models.Index(fields=['report_type', '-generated_at']),
            models.Index(fields=['-generated_at']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.generated_at.strftime('%Y-%m-%d')}"

