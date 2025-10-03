"""
Views for router management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from .models import Router, RouterLog
from .forms import RouterForm
from .services.mikrotik_api import MikroTikAPIService
from core.models import ActivityLog


@login_required
def router_list(request):
    """List all routers with their status."""
    routers = Router.objects.annotate(
        log_count=Count('logs')
    ).order_by('name')
    
    context = {
        'routers': routers,
        'total_routers': routers.count(),
        'online_routers': routers.filter(status='ONLINE').count(),
        'offline_routers': routers.filter(status='OFFLINE').count(),
    }
    
    return render(request, 'routers/router_list.html', context)


@login_required
def router_create(request):
    """Create a new router."""
    if request.method == 'POST':
        form = RouterForm(request.POST)
        if form.is_valid():
            router = form.save(commit=False)
            router.created_by = request.user
            router.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Router',
                object_id=router.id.int if hasattr(router.id, 'int') else None,
                description=f"Created router: {router.name}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, f"Router '{router.name}' created successfully!")
            return redirect('routers:router_detail', router_id=router.id)
    else:
        form = RouterForm()
    
    context = {
        'form': form,
        'title': 'Add New Router',
    }
    
    return render(request, 'routers/router_form.html', context)


@login_required
def router_detail(request, router_id):
    """View router details and logs."""
    router = get_object_or_404(Router, id=router_id)
    recent_logs = router.logs.all()[:20]
    
    # Get router statistics
    from customers.models import Customer
    customers = Customer.objects.filter(router=router)
    
    context = {
        'router': router,
        'recent_logs': recent_logs,
        'total_customers': customers.count(),
        'active_customers': customers.filter(is_active=True).count(),
        'disabled_customers': customers.filter(is_active=False).count(),
    }
    
    return render(request, 'routers/router_detail.html', context)


@login_required
def router_edit(request, router_id):
    """Edit an existing router."""
    router = get_object_or_404(Router, id=router_id)
    
    if request.method == 'POST':
        form = RouterForm(request.POST, instance=router)
        if form.is_valid():
            router = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Router',
                object_id=router.id.int if hasattr(router.id, 'int') else None,
                description=f"Updated router: {router.name}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, f"Router '{router.name}' updated successfully!")
            return redirect('routers:router_detail', router_id=router.id)
    else:
        form = RouterForm(instance=router)
    
    context = {
        'form': form,
        'router': router,
        'title': f'Edit Router: {router.name}',
    }
    
    return render(request, 'routers/router_form.html', context)


@login_required
@require_POST
def router_delete(request, router_id):
    """Delete a router."""
    router = get_object_or_404(Router, id=router_id)
    router_name = router.name
    
    # Log activity before deletion
    ActivityLog.objects.create(
        user=request.user,
        action='DELETE',
        model_name='Router',
        description=f"Deleted router: {router_name}",
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    
    router.delete()
    messages.success(request, f"Router '{router_name}' deleted successfully!")
    
    return redirect('routers:router_list')


@login_required
def router_test_connection(request, router_id):
    """Test connection to a router."""
    router = get_object_or_404(Router, id=router_id)
    
    api_service = MikroTikAPIService(router)
    is_online, info = api_service.check_status()
    
    if is_online:
        router.update_status('ONLINE')
        
        # Update router info
        if 'version' in info:
            router.router_version = info['version']
        if 'board_name' in info:
            router.router_model = info['board_name']
        if 'identity' in info:
            router.router_identity = info['identity']
        router.save()
        
        messages.success(request, f"Router '{router.name}' is ONLINE!")
    else:
        router.update_status('OFFLINE')
        error_msg = info.get('error', 'Unknown error')
        messages.error(request, f"Router '{router.name}' is OFFLINE: {error_msg}")
    
    return redirect('routers:router_detail', router_id=router.id)


@login_required
def router_status_ajax(request, router_id):
    """AJAX endpoint to check router status."""
    router = get_object_or_404(Router, id=router_id)
    
    api_service = MikroTikAPIService(router)
    is_online, info = api_service.check_status()
    
    if is_online:
        router.update_status('ONLINE')
        status_data = {
            'status': 'ONLINE',
            'status_class': 'bg-green-500',
            'info': info,
        }
    else:
        router.update_status('OFFLINE')
        status_data = {
            'status': 'OFFLINE',
            'status_class': 'bg-red-500',
            'error': info.get('error', 'Connection failed'),
        }
    
    return JsonResponse(status_data)


@login_required
def router_logs(request, router_id):
    """View all logs for a router."""
    router = get_object_or_404(Router, id=router_id)
    logs = router.logs.all()
    
    # Filter by log type if specified
    log_type = request.GET.get('type')
    if log_type:
        logs = logs.filter(log_type=log_type)
    
    context = {
        'router': router,
        'logs': logs,
        'log_types': RouterLog.LOG_TYPES,
    }
    
    return render(request, 'routers/router_logs.html', context)

