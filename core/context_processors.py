"""
Context processors for making data available in all templates.
"""
from django.db.models import Count
from .models import Notification


def site_settings(request):
    """
    Add site-wide settings and user notifications to template context.
    """
    context = {
        'site_name': 'MikroTik Billing',
        'site_version': '1.0.0',
    }
    
    if request.user.is_authenticated:
        # Get unread notifications count
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        context['unread_notifications_count'] = unread_notifications
        
        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            user=request.user
        )[:5]
        
        context['recent_notifications'] = recent_notifications
    
    return context

