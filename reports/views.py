"""
Views for reports and analytics.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import Report
from customers.models import Customer, CustomerSession
from payments.models import Payment
from routers.models import Router
from profiles.models import Profile
from vouchers.models import Voucher


@login_required
def reports_dashboard(request):
    """Main reports and analytics dashboard."""
    
    # Get date range (default: last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Revenue statistics
    revenue_stats = Payment.objects.filter(
        status='COMPLETED',
        completed_at__gte=start_date,
        completed_at__lte=end_date
    ).aggregate(
        total_revenue=Sum('amount'),
        total_payments=Count('id'),
        avg_payment=Avg('amount')
    )
    
    # Customer statistics
    customer_stats = {
        'total_customers': Customer.objects.count(),
        'active_customers': Customer.objects.filter(is_active=True).count(),
        'new_customers': Customer.objects.filter(created_at__gte=start_date).count(),
        'expired_customers': Customer.objects.filter(status='EXPIRED').count(),
    }
    
    # Router statistics
    router_stats = {
        'total_routers': Router.objects.count(),
        'online_routers': Router.objects.filter(status='ONLINE').count(),
        'offline_routers': Router.objects.filter(status='OFFLINE').count(),
    }
    
    # Payment methods breakdown
    payment_methods = Payment.objects.filter(
        status='COMPLETED',
        completed_at__gte=start_date
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    )
    
    # Profile popularity
    popular_profiles = Profile.objects.annotate(
        customer_count=Count('customer', filter=Q(customer__is_active=True))
    ).order_by('-customer_count')[:5]
    
    # Daily revenue chart data (last 7 days)
    daily_revenue = []
    for i in range(7):
        date = end_date - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        revenue = Payment.objects.filter(
            status='COMPLETED',
            completed_at__gte=day_start,
            completed_at__lt=day_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        daily_revenue.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'revenue': float(revenue)
        })
    
    daily_revenue.reverse()
    
    context = {
        'revenue_stats': revenue_stats,
        'customer_stats': customer_stats,
        'router_stats': router_stats,
        'payment_methods': payment_methods,
        'popular_profiles': popular_profiles,
        'daily_revenue': json.dumps(daily_revenue),
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def revenue_report(request):
    """Detailed revenue report."""
    # Get date range from request
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all completed payments in range
    payments = Payment.objects.filter(
        status='COMPLETED',
        completed_at__gte=start_date,
        completed_at__lte=end_date
    ).select_related('customer', 'profile')
    
    # Calculate totals
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_payments = payments.count()
    
    # Group by payment method
    by_method = payments.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    )
    
    # Group by profile
    by_profile = payments.values('profile__name').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    # Group by router
    by_router = payments.values('customer__router__name').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'total_payments': total_payments,
        'by_method': by_method,
        'by_profile': by_profile,
        'by_router': by_router,
        'start_date': start_date,
        'end_date': end_date,
        'days': days,
    }
    
    return render(request, 'reports/revenue_report.html', context)


@login_required
def customer_report(request):
    """Detailed customer analytics report."""
    # Get all customers with related data
    customers = Customer.objects.select_related('router', 'profile').all()
    
    # Statistics
    stats = {
        'total': customers.count(),
        'active': customers.filter(is_active=True).count(),
        'expired': customers.filter(status='EXPIRED').count(),
        'disabled': customers.filter(status='DISABLED').count(),
        'pending': customers.filter(status='PENDING').count(),
    }
    
    # By router
    by_router = customers.values('router__name').annotate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True))
    ).order_by('-total')
    
    # By profile
    by_profile = customers.values('profile__name').annotate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True))
    ).order_by('-total')
    
    # Expiring soon (next 7 days)
    expiring_soon = customers.filter(
        is_active=True,
        expires_at__gte=timezone.now(),
        expires_at__lte=timezone.now() + timedelta(days=7)
    ).order_by('expires_at')
    
    context = {
        'stats': stats,
        'by_router': by_router,
        'by_profile': by_profile,
        'expiring_soon': expiring_soon,
    }
    
    return render(request, 'reports/customer_report.html', context)


@login_required
def router_report(request):
    """Router performance and statistics report."""
    routers = Router.objects.annotate(
        customer_count=Count('customers'),
        active_customer_count=Count('customers', filter=Q(customers__is_active=True))
    ).all()
    
    context = {
        'routers': routers,
    }
    
    return render(request, 'reports/router_report.html', context)


@login_required
def saved_reports_list(request):
    """List all saved reports."""
    reports = Report.objects.all()
    
    context = {
        'reports': reports,
    }
    
    return render(request, 'reports/saved_reports.html', context)


@login_required
def saved_report_detail(request, report_id):
    """View a saved report."""
    report = get_object_or_404(Report, id=report_id)
    
    context = {
        'report': report,
    }
    
    return render(request, 'reports/saved_report_detail.html', context)

