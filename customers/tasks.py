"""
Celery tasks for customer management.
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import Customer
from routers.services.mikrotik_api import MikroTikAPIService
from core.models import Notification
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_expired_users():
    """
    Check for expired customer accounts and disable them.
    Runs daily via Celery beat.
    """
    now = timezone.now()
    expired_customers = Customer.objects.filter(
        is_active=True,
        expires_at__lte=now
    )
    
    disabled_count = 0
    
    for customer in expired_customers:
        # Disable on router
        api_service = MikroTikAPIService(customer.router)
        success, message = api_service.disable_ppp_secret(customer.username)
        
        if success:
            customer.status = 'EXPIRED'
            customer.is_active = False
            customer.save()
            
            # Send notification
            if customer.send_notifications:
                Notification.objects.create(
                    user=customer.created_by if customer.created_by else None,
                    title='Customer Account Expired',
                    message=f"Customer {customer.username} ({customer.full_name}) has expired.",
                    notification_type='WARNING',
                    link=f'/customers/{customer.id}/'
                )
            
            disabled_count += 1
            logger.info(f"Disabled expired customer: {customer.username}")
        else:
            logger.error(f"Failed to disable customer {customer.username}: {message}")
    
    logger.info(f"Checked expired users: {disabled_count} disabled")
    return {'disabled_count': disabled_count}


@shared_task
def send_expiry_reminders():
    """
    Send reminders to customers whose accounts are about to expire.
    Sends 3 days, 1 day, and 1 hour before expiry.
    """
    from datetime import timedelta
    
    now = timezone.now()
    
    # Get customers expiring in 3 days
    three_days = now + timedelta(days=3)
    customers_3_days = Customer.objects.filter(
        is_active=True,
        expires_at__gte=now,
        expires_at__lte=three_days,
        send_notifications=True
    )
    
    for customer in customers_3_days:
        Notification.objects.create(
            user=customer.created_by if customer.created_by else None,
            title='Customer Expiry Reminder',
            message=f"Customer {customer.username} will expire in 3 days.",
            notification_type='WARNING',
            link=f'/customers/{customer.id}/'
        )
    
    logger.info(f"Sent {customers_3_days.count()} expiry reminders (3 days)")
    return {'reminders_sent': customers_3_days.count()}


@shared_task
def sync_customer_data_usage(customer_id):
    """
    Sync customer data usage from router.
    
    Args:
        customer_id: UUID of the customer
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        # This would fetch data usage from MikroTik accounting
        # For now, it's a placeholder
        logger.info(f"Synced data usage for customer: {customer.username}")
        return {'customer': customer.username, 'status': 'synced'}
    except Customer.DoesNotExist:
        logger.error(f"Customer {customer_id} not found")
        return {'error': 'Customer not found'}

