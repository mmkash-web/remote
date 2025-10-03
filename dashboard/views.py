"""
Views for main dashboard.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from customers.models import Customer
from payments.models import Payment
from routers.models import Router
from profiles.models import Profile
from core.models import ActivityLog


@login_required
def home(request):
    """Main dashboard homepage."""
    
    # Quick statistics
    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(is_active=True).count()
    total_routers = Router.objects.count()
    online_routers = Router.objects.filter(status='ONLINE').count()
    
    # Revenue (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    revenue_30_days = Payment.objects.filter(
        status='COMPLETED',
        completed_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Today's statistics
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = Payment.objects.filter(
        status='COMPLETED',
        completed_at__gte=today_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    today_payments = Payment.objects.filter(
        status='COMPLETED',
        completed_at__gte=today_start
    ).count()
    
    new_customers_today = Customer.objects.filter(created_at__gte=today_start).count()
    
    # Recent activity
    recent_activity = ActivityLog.objects.select_related('user').all()[:10]
    
    # Expiring soon (next 3 days)
    expiring_soon = Customer.objects.filter(
        is_active=True,
        expires_at__gte=timezone.now(),
        expires_at__lte=timezone.now() + timedelta(days=3)
    ).select_related('router', 'profile').order_by('expires_at')[:10]
    
    # Recent payments
    recent_payments = Payment.objects.filter(
        status='COMPLETED'
    ).select_related('customer', 'profile').order_by('-completed_at')[:10]
    
    # Routers status
    routers = Router.objects.annotate(
        customer_count=Count('customers', filter=Q(customers__is_active=True))
    ).all()[:10]
    
    context = {
        'total_customers': total_customers,
        'active_customers': active_customers,
        'total_routers': total_routers,
        'online_routers': online_routers,
        'revenue_30_days': revenue_30_days,
        'today_revenue': today_revenue,
        'today_payments': today_payments,
        'new_customers_today': new_customers_today,
        'recent_activity': recent_activity,
        'expiring_soon': expiring_soon,
        'recent_payments': recent_payments,
        'routers': routers,
    }
    
    return render(request, 'dashboard/home.html', context)


def index(request):
    """Root index - redirect to dashboard if logged in, else to login."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('login')

