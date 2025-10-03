"""
Views for voucher management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Q
import csv

from .models import Voucher, VoucherBatch
from routers.models import Router
from profiles.models import Profile
from customers.models import Customer
from core.models import ActivityLog


@login_required
def voucher_batch_list(request):
    """List all voucher batches."""
    batches = VoucherBatch.objects.select_related('profile', 'router', 'created_by').annotate(
        used_count=Count('vouchers', filter=Q(vouchers__is_used=True)),
        available_count=Count('vouchers', filter=Q(vouchers__is_used=False, vouchers__is_active=True))
    )
    
    context = {
        'batches': batches,
        'total_batches': batches.count(),
    }
    
    return render(request, 'vouchers/batch_list.html', context)


@login_required
def voucher_batch_create(request):
    """Create a new voucher batch."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        profile_id = request.POST.get('profile')
        router_id = request.POST.get('router')
        quantity = int(request.POST.get('quantity', 0))
        price = request.POST.get('price')
        
        try:
            profile = Profile.objects.get(id=profile_id)
            router = Router.objects.get(id=router_id)
            
            # Create batch
            batch = VoucherBatch.objects.create(
                name=name,
                description=description,
                profile=profile,
                router=router,
                quantity=quantity,
                price_per_voucher=price,
                created_by=request.user,
            )
            
            # Generate vouchers
            vouchers_created = 0
            for _ in range(quantity):
                # Generate unique code
                while True:
                    code = Voucher.generate_code()
                    if not Voucher.objects.filter(code=code).exists():
                        break
                
                Voucher.objects.create(
                    code=code,
                    batch=batch,
                    profile=profile,
                    router=router,
                )
                vouchers_created += 1
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='VoucherBatch',
                description=f"Created voucher batch: {name} with {vouchers_created} vouchers",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, f"Created batch '{name}' with {vouchers_created} vouchers!")
            return redirect('vouchers:batch_detail', batch_id=batch.id)
        
        except (Profile.DoesNotExist, Router.DoesNotExist):
            messages.error(request, "Invalid profile or router selected.")
        except ValueError:
            messages.error(request, "Invalid quantity or price.")
    
    profiles = Profile.objects.filter(is_active=True)
    routers = Router.objects.filter(is_active=True)
    
    context = {
        'profiles': profiles,
        'routers': routers,
    }
    
    return render(request, 'vouchers/batch_create.html', context)


@login_required
def voucher_batch_detail(request, batch_id):
    """View voucher batch details."""
    batch = get_object_or_404(
        VoucherBatch.objects.select_related('profile', 'router', 'created_by'),
        id=batch_id
    )
    vouchers = batch.vouchers.all()[:100]  # Show first 100
    
    context = {
        'batch': batch,
        'vouchers': vouchers,
        'total_vouchers': batch.vouchers.count(),
        'used_vouchers': batch.vouchers.filter(is_used=True).count(),
        'available_vouchers': batch.vouchers.filter(is_used=False, is_active=True).count(),
    }
    
    return render(request, 'vouchers/batch_detail.html', context)


@login_required
def voucher_batch_export(request, batch_id):
    """Export vouchers as CSV."""
    batch = get_object_or_404(VoucherBatch, id=batch_id)
    vouchers = batch.vouchers.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="vouchers_{batch.name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Voucher Code', 'Profile', 'Router', 'Price', 'Status', 'Created'])
    
    for voucher in vouchers:
        status = 'Used' if voucher.is_used else ('Active' if voucher.is_active else 'Inactive')
        writer.writerow([
            voucher.code,
            voucher.profile.name,
            voucher.router.name,
            batch.price_per_voucher,
            status,
            voucher.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    
    return response


@login_required
def voucher_redeem(request):
    """Redeem a voucher code for a customer."""
    if request.method == 'POST':
        voucher_code = request.POST.get('voucher_code', '').strip().upper()
        customer_id = request.POST.get('customer_id')
        
        try:
            voucher = Voucher.objects.get(code=voucher_code)
            customer = Customer.objects.get(id=customer_id)
            
            if not voucher.is_valid():
                if voucher.is_used:
                    messages.error(request, f"Voucher {voucher_code} has already been used.")
                elif not voucher.is_active:
                    messages.error(request, f"Voucher {voucher_code} is not active.")
                else:
                    messages.error(request, f"Voucher {voucher_code} has expired.")
            else:
                # Mark voucher as used
                voucher.mark_as_used(customer, request.META.get('REMOTE_ADDR'))
                
                # Extend customer subscription
                customer.extend_subscription()
                
                # Enable if disabled
                if not customer.is_active:
                    from routers.services.mikrotik_api import MikroTikAPIService
                    api_service = MikroTikAPIService(customer.router)
                    api_service.enable_ppp_secret(customer.username)
                
                # Log activity
                ActivityLog.objects.create(
                    user=request.user,
                    action='PAYMENT',
                    model_name='Voucher',
                    description=f"Redeemed voucher {voucher_code} for customer {customer.username}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                )
                
                messages.success(
                    request,
                    f"Voucher redeemed successfully! Customer {customer.username} "
                    f"extended until {customer.expires_at.strftime('%Y-%m-%d %H:%M')}"
                )
                return redirect('customers:customer_detail', customer_id=customer.id)
        
        except Voucher.DoesNotExist:
            messages.error(request, f"Voucher code '{voucher_code}' not found.")
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found.")
    
    customers = Customer.objects.all()
    
    context = {
        'customers': customers,
    }
    
    return render(request, 'vouchers/redeem.html', context)


@login_required
def voucher_list(request):
    """List all vouchers with filtering."""
    vouchers = Voucher.objects.select_related('batch', 'profile', 'router', 'used_by')
    
    # Apply filters
    status = request.GET.get('status')
    if status == 'used':
        vouchers = vouchers.filter(is_used=True)
    elif status == 'available':
        vouchers = vouchers.filter(is_used=False, is_active=True)
    
    batch_id = request.GET.get('batch')
    if batch_id:
        vouchers = vouchers.filter(batch_id=batch_id)
    
    context = {
        'vouchers': vouchers[:200],  # Limit to 200 for performance
        'total_vouchers': vouchers.count(),
        'used_vouchers': Voucher.objects.filter(is_used=True).count(),
        'available_vouchers': Voucher.objects.filter(is_used=False, is_active=True).count(),
    }
    
    return render(request, 'vouchers/voucher_list.html', context)

