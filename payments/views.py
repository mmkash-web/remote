"""
Views for payment management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import timedelta
from django.utils import timezone

from .models import Payment, PaymentGatewayLog
from customers.models import Customer
from core.models import ActivityLog


@login_required
def payment_list(request):
    """List all payments with filtering."""
    payments = Payment.objects.select_related('customer', 'profile').all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    date_range = request.GET.get('date_range', '30')
    try:
        days = int(date_range)
        start_date = timezone.now() - timedelta(days=days)
        payments = payments.filter(created_at__gte=start_date)
    except ValueError:
        pass
    
    # Calculate statistics
    total_payments = payments.count()
    completed_payments = payments.filter(status='COMPLETED')
    total_revenue = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
    pending_payments = payments.filter(status='PENDING').count()
    
    context = {
        'payments': payments,
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'completed_count': completed_payments.count(),
        'status_filter': status_filter,
        'method_filter': method_filter,
        'date_range': date_range,
    }
    
    return render(request, 'payments/payment_list.html', context)


@login_required
def payment_detail(request, payment_id):
    """View payment details."""
    payment = get_object_or_404(
        Payment.objects.select_related('customer', 'profile', 'processed_by'),
        id=payment_id
    )
    gateway_logs = payment.gateway_logs.all()
    
    context = {
        'payment': payment,
        'gateway_logs': gateway_logs,
    }
    
    return render(request, 'payments/payment_detail.html', context)


@login_required
def payment_manual_create(request, customer_id):
    """Create a manual payment (cash, bank transfer, etc.)."""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        reference_code = request.POST.get('reference_code', '')
        notes = request.POST.get('notes', '')
        
        try:
            amount = float(amount)
            
            # Create payment
            payment = Payment.objects.create(
                customer=customer,
                profile=customer.profile,
                amount=amount,
                currency=customer.profile.currency,
                payment_method=payment_method,
                reference_code=reference_code,
                notes=notes,
                processed_by=request.user,
            )
            
            # Mark as completed
            payment.mark_completed()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='PAYMENT',
                model_name='Payment',
                description=f"Recorded manual payment for {customer.username}: {amount}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(
                request,
                f"Payment of {customer.profile.currency} {amount} recorded successfully! "
                f"Customer {customer.username} has been activated/extended."
            )
            return redirect('customers:customer_detail', customer_id=customer.id)
            
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount provided.")
    
    context = {
        'customer': customer,
    }
    
    return render(request, 'payments/payment_manual_create.html', context)


@login_required
def payment_mark_completed(request, payment_id):
    """Manually mark a payment as completed."""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'COMPLETED':
        messages.warning(request, "Payment is already completed.")
    else:
        payment.processed_by = request.user
        payment.mark_completed()
        
        ActivityLog.objects.create(
            user=request.user,
            action='PAYMENT',
            model_name='Payment',
            description=f"Manually completed payment {payment.id} for {payment.customer.username}",
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        messages.success(request, "Payment marked as completed and customer activated!")
    
    return redirect('payments:payment_detail', payment_id=payment.id)


@login_required
def payment_mark_failed(request, payment_id):
    """Mark a payment as failed."""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        payment.mark_failed(reason)
        
        ActivityLog.objects.create(
            user=request.user,
            action='PAYMENT',
            model_name='Payment',
            description=f"Marked payment {payment.id} as failed",
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        messages.success(request, "Payment marked as failed.")
        return redirect('payments:payment_detail', payment_id=payment.id)
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/payment_mark_failed.html', context)

