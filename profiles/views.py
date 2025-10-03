"""
Views for profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import Profile
from .forms import ProfileForm
from core.models import ActivityLog


@login_required
def profile_list(request):
    """List all profiles."""
    profiles = Profile.objects.annotate(
        customer_count=Count('customer')
    ).order_by('price')
    
    context = {
        'profiles': profiles,
        'total_profiles': profiles.count(),
        'active_profiles': profiles.filter(is_active=True).count(),
    }
    
    return render(request, 'profiles/profile_list.html', context)


@login_required
def profile_create(request):
    """Create a new profile."""
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.created_by = request.user
            profile.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Profile',
                description=f"Created profile: {profile.name}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, f"Profile '{profile.name}' created successfully!")
            return redirect('profiles:profile_list')
    else:
        form = ProfileForm()
    
    context = {
        'form': form,
        'title': 'Add New Profile',
    }
    
    return render(request, 'profiles/profile_form.html', context)


@login_required
def profile_detail(request, profile_id):
    """View profile details."""
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Get customers using this profile
    from customers.models import Customer
    customers = Customer.objects.filter(profile=profile)
    
    context = {
        'profile': profile,
        'customers': customers[:20],  # Show recent 20
        'total_customers': customers.count(),
        'active_customers': customers.filter(is_active=True).count(),
    }
    
    return render(request, 'profiles/profile_detail.html', context)


@login_required
def profile_edit(request, profile_id):
    """Edit an existing profile."""
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Profile',
                description=f"Updated profile: {profile.name}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, f"Profile '{profile.name}' updated successfully!")
            return redirect('profiles:profile_detail', profile_id=profile.id)
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'title': f'Edit Profile: {profile.name}',
    }
    
    return render(request, 'profiles/profile_form.html', context)


@login_required
def profile_delete(request, profile_id):
    """Delete a profile."""
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Check if profile has customers
    from customers.models import Customer
    if Customer.objects.filter(profile=profile).exists():
        messages.error(
            request,
            f"Cannot delete profile '{profile.name}' because it has active customers. "
            "Please reassign or delete the customers first."
        )
        return redirect('profiles:profile_detail', profile_id=profile.id)
    
    profile_name = profile.name
    
    # Log activity before deletion
    ActivityLog.objects.create(
        user=request.user,
        action='DELETE',
        model_name='Profile',
        description=f"Deleted profile: {profile_name}",
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    
    profile.delete()
    messages.success(request, f"Profile '{profile_name}' deleted successfully!")
    
    return redirect('profiles:profile_list')

