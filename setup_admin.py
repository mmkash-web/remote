#!/usr/bin/env python
"""
Quick setup script for MikroTik Billing System.
Creates initial superuser and sample data for testing.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrotik_billing.settings')
django.setup()

from django.contrib.auth.models import User
from profiles.models import Profile
from decimal import Decimal


def create_superuser():
    """Create default superuser if it doesn't exist."""
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'
    
    if User.objects.filter(username=username).exists():
        print(f"✓ Superuser '{username}' already exists")
        return
    
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✓ Created superuser: {username} / {password}")
    print(f"  IMPORTANT: Change this password in production!")


def create_sample_profiles():
    """Create sample bandwidth profiles."""
    profiles_data = [
        {
            'name': '5Mbps Daily',
            'description': '5Mbps speed for 1 day',
            'download_speed': '5M',
            'upload_speed': '5M',
            'duration_value': 1,
            'duration_unit': 'DAYS',
            'price': Decimal('50.00'),
            'currency': 'KES',
        },
        {
            'name': '10Mbps Weekly',
            'description': '10Mbps speed for 7 days',
            'download_speed': '10M',
            'upload_speed': '10M',
            'duration_value': 7,
            'duration_unit': 'DAYS',
            'price': Decimal('300.00'),
            'currency': 'KES',
        },
        {
            'name': '20Mbps Monthly',
            'description': '20Mbps speed for 30 days',
            'download_speed': '20M',
            'upload_speed': '20M',
            'duration_value': 1,
            'duration_unit': 'MONTHS',
            'price': Decimal('1000.00'),
            'currency': 'KES',
        },
    ]
    
    for profile_data in profiles_data:
        profile, created = Profile.objects.get_or_create(
            name=profile_data['name'],
            defaults=profile_data
        )
        if created:
            print(f"✓ Created profile: {profile.name}")
        else:
            print(f"  Profile '{profile.name}' already exists")


def main():
    """Run setup tasks."""
    print("\n" + "="*60)
    print("MikroTik Billing System - Quick Setup")
    print("="*60 + "\n")
    
    print("Setting up initial data...\n")
    
    # Create superuser
    create_superuser()
    print()
    
    # Create sample profiles
    create_sample_profiles()
    print()
    
    print("="*60)
    print("Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000")
    print("3. Login with: admin / admin123")
    print("4. Add your first router")
    print("5. Create customers and start managing!")
    print("\n✨ Happy billing!\n")


if __name__ == '__main__':
    main()

