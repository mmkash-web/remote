"""
Celery tasks for generating reports.
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
import logging

from .models import Report
from payments.models import Payment
from customers.models import Customer

logger = logging.getLogger(__name__)


@shared_task
def generate_daily_report():
    """
    Generate daily report automatically.
    Runs every day at 11:55 PM via Celery beat.
    """
    end_date = timezone.now()
    start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Revenue data
    revenue_data = Payment.objects.filter(
        status='COMPLETED',
        completed_at__gte=start_date,
        completed_at__lt=end_date
    ).aggregate(
        total_revenue=Sum('amount'),
        total_payments=Count('id')
    )
    
    # Customer data
    customer_data = {
        'new_customers': Customer.objects.filter(created_at__gte=start_date).count(),
        'active_customers': Customer.objects.filter(is_active=True).count(),
    }
    
    # Create report
    report_data = {
        'revenue': revenue_data,
        'customers': customer_data,
    }
    
    summary = (
        f"Daily Report for {start_date.strftime('%Y-%m-%d')}\n"
        f"Revenue: {revenue_data['total_revenue'] or 0}\n"
        f"Payments: {revenue_data['total_payments']}\n"
        f"New Customers: {customer_data['new_customers']}"
    )
    
    report = Report.objects.create(
        report_type='DAILY',
        title=f"Daily Report - {start_date.strftime('%Y-%m-%d')}",
        start_date=start_date,
        end_date=end_date,
        data=report_data,
        summary=summary,
    )
    
    logger.info(f"Generated daily report: {report.id}")
    return {'report_id': str(report.id)}

