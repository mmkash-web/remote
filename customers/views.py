"""
Views for customer management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.views.decorators.http import require_POST

from .models import Customer, CustomerSession
from .forms import CustomerForm, CustomerQuickEditForm, CustomerExtendForm
from routers.services.mikrotik_api import MikroTikAPIService
from core.models import ActivityLog, Notification


@login_required
def customer_list(request):
    """List all customers with filtering."""
    customers = Customer.objects.select_related('router', 'profile').all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        customers = customers.filter(status=status_filter)
    
    router_filter = request.GET.get('router')
    if router_filter:
        customers = customers.filter(router_id=router_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Get statistics
    total_customers = customers.count()
    active_customers = customers.filter(is_active=True).count()
    expired_customers = customers.filter(status='EXPIRED').count()
    
    context = {
        'customers': customers,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'expired_customers': expired_customers,
        'status_filter': status_filter,
        'router_filter': router_filter,
        'search_query': search_query,
    }
    
    return render(request, 'customers/customer_list.html', context)


@login_required
def customer_create(request):
    """Create a new customer."""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            
            # Create user on router via API
            api_service = MikroTikAPIService(customer.router)
            success, message = api_service.create_ppp_secret(
                username=customer.username,
                password=customer.password,
                profile=customer.profile.get_mikrotik_profile_name()
            )
            
            if success:
                messages.success(request, f"Customer '{customer.username}' created successfully on router!")
            else:
                messages.warning(
                    request,
                    f"Customer created in database but failed to create on router: {message}"
                )
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Customer',
                description=f"Created customer: {customer.username}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return redirect('customers:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': 'Add New Customer',
    }
    
    return render(request, 'customers/customer_form.html', context)


@login_required
def customer_detail(request, customer_id):
    """View customer details."""
    customer = get_object_or_404(Customer.objects.select_related('router', 'profile'), id=customer_id)
    recent_sessions = customer.sessions.all()[:10]
    
    # Get payment history
    from payments.models import Payment
    payments = Payment.objects.filter(customer=customer).order_by('-created_at')[:10]
    
    context = {
        'customer': customer,
        'recent_sessions': recent_sessions,
        'payments': payments,
        'total_sessions': customer.sessions.count(),
        'total_payments': payments.count(),
    }
    
    return render(request, 'customers/customer_detail.html', context)


@login_required
def customer_edit(request, customer_id):
    """Edit an existing customer."""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            old_profile = customer.profile
            customer = form.save()
            
            # If profile changed, update on router
            if old_profile != customer.profile:
                api_service = MikroTikAPIService(customer.router)
                api_service.update_ppp_secret(
                    username=customer.username,
                    profile=customer.profile.get_mikrotik_profile_name()
                )
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Customer',
                description=f"Updated customer: {customer.username}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, f"Customer '{customer.username}' updated successfully!")
            return redirect('customers:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': f'Edit Customer: {customer.username}',
    }
    
    return render(request, 'customers/customer_form.html', context)


@login_required
@require_POST
def customer_delete(request, customer_id):
    """Delete a customer."""
    customer = get_object_or_404(Customer, id=customer_id)
    customer_username = customer.username
    
    # Delete from router
    api_service = MikroTikAPIService(customer.router)
    api_service.delete_ppp_secret(customer.username)
    
    # Log activity before deletion
    ActivityLog.objects.create(
        user=request.user,
        action='DELETE',
        model_name='Customer',
        description=f"Deleted customer: {customer_username}",
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    
    customer.delete()
    messages.success(request, f"Customer '{customer_username}' deleted successfully!")
    
    return redirect('customers:customer_list')


@login_required
@require_POST
def customer_enable(request, customer_id):
    """Enable a customer account."""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Enable on router
    api_service = MikroTikAPIService(customer.router)
    success, message = api_service.enable_ppp_secret(customer.username)
    
    if success:
        customer.is_active = True
        customer.status = 'ACTIVE'
        customer.save()
        
        ActivityLog.objects.create(
            user=request.user,
            action='ENABLE',
            model_name='Customer',
            description=f"Enabled customer: {customer.username}",
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        messages.success(request, f"Customer '{customer.username}' enabled successfully!")
    else:
        messages.error(request, f"Failed to enable customer: {message}")
    
    return redirect('customers:customer_detail', customer_id=customer.id)


@login_required
@require_POST
def customer_disable(request, customer_id):
    """Disable a customer account."""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Disable on router
    api_service = MikroTikAPIService(customer.router)
    success, message = api_service.disable_ppp_secret(customer.username)
    
    if success:
        customer.disable()
        
        ActivityLog.objects.create(
            user=request.user,
            action='DISABLE',
            model_name='Customer',
            description=f"Disabled customer: {customer.username}",
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        messages.success(request, f"Customer '{customer.username}' disabled successfully!")
    else:
        messages.error(request, f"Failed to disable customer: {message}")
    
    return redirect('customers:customer_detail', customer_id=customer.id)


@login_required
def customer_extend(request, customer_id):
    """Extend customer subscription."""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerExtendForm(request.POST)
        if form.is_valid():
            extend_option = form.cleaned_data['extend_option']
            
            if extend_option == 'custom':
                days = form.cleaned_data['custom_days']
                customer.extend_subscription(additional_days=days)
            else:
                customer.extend_subscription()
            
            # Enable if disabled
            if not customer.is_active:
                api_service = MikroTikAPIService(customer.router)
                api_service.enable_ppp_secret(customer.username)
            
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Customer',
                description=f"Extended subscription for customer: {customer.username}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(
                request,
                f"Subscription extended! New expiry: {customer.expires_at.strftime('%Y-%m-%d %H:%M')}"
            )
            return redirect('customers:customer_detail', customer_id=customer.id)
    else:
        form = CustomerExtendForm()
    
    context = {
        'form': form,
        'customer': customer,
    }
    
    return render(request, 'customers/customer_extend.html', context)


@login_required
def customer_sessions(request, customer_id):
    """View all sessions for a customer."""
    customer = get_object_or_404(Customer, id=customer_id)
    sessions = customer.sessions.all()
    
    context = {
        'customer': customer,
        'sessions': sessions,
    }
    
    return render(request, 'customers/customer_sessions.html', context)


@login_required
def active_sessions_view(request):
    """View all currently active sessions."""
    # Get all active routers
    from routers.models import Router
    routers = Router.objects.filter(is_active=True, status='ONLINE')
    
    all_active_sessions = []
    
    for router in routers:
        api_service = MikroTikAPIService(router)
        success, connections = api_service.get_active_connections()
        
        if success:
            for conn in connections:
                # Try to match with customer
                try:
                    customer = Customer.objects.get(username=conn['name'], router=router)
                    conn['customer'] = customer
                except Customer.DoesNotExist:
                    conn['customer'] = None
                
                conn['router'] = router
                all_active_sessions.append(conn)
    
    context = {
        'active_sessions': all_active_sessions,
        'total_active': len(all_active_sessions),
    }
    
    return render(request, 'customers/active_sessions.html', context)

