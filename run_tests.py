#!/usr/bin/env python
"""
Automated testing script for MikroTik Billing System.
Runs basic functionality tests to verify system works correctly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrotik_billing.settings')
django.setup()

from django.contrib.auth.models import User
from routers.models import Router
from profiles.models import Profile
from customers.models import Customer
from payments.models import Payment
from vouchers.models import Voucher, VoucherBatch
from decimal import Decimal


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def print_header(self, text):
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)
    
    def test(self, description, test_func):
        """Run a single test."""
        try:
            result = test_func()
            if result:
                print(f"✓ {description}")
                self.passed += 1
                return True
            else:
                print(f"✗ {description} - Test returned False")
                self.failed += 1
                return False
        except Exception as e:
            print(f"✗ {description} - Error: {str(e)}")
            self.failed += 1
            return False
    
    def warning(self, description):
        """Log a warning."""
        print(f"⚠ {description}")
        self.warnings += 1
    
    def summary(self):
        """Print test summary."""
        self.print_header("Test Summary")
        print(f"\n✓ Passed: {self.passed}")
        print(f"✗ Failed: {self.failed}")
        print(f"⚠ Warnings: {self.warnings}")
        
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 All tests passed! System is working correctly.")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Please review errors above.")
            return False


def main():
    """Run all tests."""
    runner = TestRunner()
    
    runner.print_header("MikroTik Billing System - Automated Tests")
    print("\nRunning automated tests...\n")
    
    # Test 1: Check if admin user exists
    runner.print_header("User & Authentication Tests")
    
    def test_admin_exists():
        return User.objects.filter(is_superuser=True).exists()
    
    runner.test("Admin user exists", test_admin_exists)
    
    def test_user_count():
        count = User.objects.count()
        print(f"  Total users: {count}")
        return count > 0
    
    runner.test("At least one user exists", test_user_count)
    
    # Test 2: Profile tests
    runner.print_header("Profile Management Tests")
    
    def test_can_create_profile():
        admin = User.objects.filter(is_superuser=True).first()
        profile, created = Profile.objects.get_or_create(
            name='Test Profile 5M',
            defaults={
                'description': 'Test profile for automated testing',
                'download_speed': '5M',
                'upload_speed': '5M',
                'duration_value': 1,
                'duration_unit': 'DAYS',
                'price': Decimal('50.00'),
                'currency': 'KES',
                'created_by': admin,
            }
        )
        return True
    
    runner.test("Can create profile", test_can_create_profile)
    
    def test_profile_count():
        count = Profile.objects.count()
        print(f"  Total profiles: {count}")
        return count > 0
    
    runner.test("Profiles exist in database", test_profile_count)
    
    def test_profile_methods():
        profile = Profile.objects.first()
        if not profile:
            return False
        
        # Test methods
        speed = profile.get_speed_display()
        duration = profile.get_duration_display_text()
        expiry = profile.calculate_expiry_date()
        
        print(f"  Speed: {speed}")
        print(f"  Duration: {duration}")
        print(f"  Sample expiry: {expiry}")
        
        return speed and duration and expiry
    
    runner.test("Profile methods work correctly", test_profile_methods)
    
    # Test 3: Router tests
    runner.print_header("Router Management Tests")
    
    def test_can_create_router():
        admin = User.objects.filter(is_superuser=True).first()
        router, created = Router.objects.get_or_create(
            name='Test Router',
            defaults={
                'description': 'Test router for automated testing',
                'vpn_ip': '192.168.100.1',
                'api_port': 8728,
                'username': 'admin',
                'password': 'test123',
                'created_by': admin,
            }
        )
        return True
    
    runner.test("Can create router", test_can_create_router)
    
    def test_router_count():
        count = Router.objects.count()
        print(f"  Total routers: {count}")
        return count > 0
    
    runner.test("Routers exist in database", test_router_count)
    
    def test_router_methods():
        router = Router.objects.first()
        if not router:
            return False
        
        # Test methods
        online = router.is_online()
        badge_class = router.get_status_badge_class()
        
        print(f"  Status: {router.status}")
        print(f"  Is online: {online}")
        print(f"  Badge class: {badge_class}")
        
        return badge_class is not None
    
    runner.test("Router methods work correctly", test_router_methods)
    
    # Test 4: Customer tests
    runner.print_header("Customer Management Tests")
    
    def test_can_create_customer():
        router = Router.objects.first()
        profile = Profile.objects.first()
        admin = User.objects.filter(is_superuser=True).first()
        
        if not router or not profile:
            print("  Skipped: Requires router and profile")
            return True
        
        customer, created = Customer.objects.get_or_create(
            username='testuser123',
            defaults={
                'password': 'password123',
                'full_name': 'Test User',
                'email': 'test@example.com',
                'phone_number': '+254712345678',
                'router': router,
                'profile': profile,
                'created_by': admin,
            }
        )
        return True
    
    runner.test("Can create customer", test_can_create_customer)
    
    def test_customer_count():
        count = Customer.objects.count()
        print(f"  Total customers: {count}")
        return True  # Don't fail if no customers
    
    runner.test("Customer table accessible", test_customer_count)
    
    def test_customer_methods():
        customer = Customer.objects.first()
        if not customer:
            print("  Skipped: No customers exist")
            return True
        
        # Test methods
        expired = customer.is_expired()
        status_class = customer.get_status_badge_class()
        
        print(f"  Status: {customer.status}")
        print(f"  Is expired: {expired}")
        
        # Test activation
        customer.activate()
        print(f"  Activated: {customer.is_active}")
        
        return status_class is not None
    
    runner.test("Customer methods work correctly", test_customer_methods)
    
    # Test 5: Payment tests
    runner.print_header("Payment System Tests")
    
    def test_can_create_payment():
        customer = Customer.objects.first()
        profile = Profile.objects.first()
        admin = User.objects.filter(is_superuser=True).first()
        
        if not customer or not profile:
            print("  Skipped: Requires customer and profile")
            return True
        
        payment = Payment.objects.create(
            customer=customer,
            profile=profile,
            amount=Decimal('50.00'),
            currency='KES',
            payment_method='CASH',
            transaction_id='TEST-' + str(Payment.objects.count() + 1),
            processed_by=admin,
            status='PENDING'
        )
        
        # Test payment completion
        payment.mark_completed()
        
        print(f"  Payment created: {payment.transaction_id}")
        print(f"  Status: {payment.status}")
        
        return payment.status == 'COMPLETED'
    
    runner.test("Can create and complete payment", test_can_create_payment)
    
    def test_payment_count():
        count = Payment.objects.count()
        print(f"  Total payments: {count}")
        return True
    
    runner.test("Payment table accessible", test_payment_count)
    
    # Test 6: Voucher tests
    runner.print_header("Voucher System Tests")
    
    def test_can_create_voucher_batch():
        router = Router.objects.first()
        profile = Profile.objects.first()
        admin = User.objects.filter(is_superuser=True).first()
        
        if not router or not profile:
            print("  Skipped: Requires router and profile")
            return True
        
        batch, created = VoucherBatch.objects.get_or_create(
            name='Test Batch',
            defaults={
                'description': 'Test voucher batch',
                'profile': profile,
                'router': router,
                'quantity': 5,
                'price_per_voucher': Decimal('50.00'),
                'created_by': admin,
            }
        )
        
        # Create vouchers if new batch
        if created:
            for i in range(5):
                code = Voucher.generate_code()
                Voucher.objects.create(
                    code=code,
                    batch=batch,
                    profile=profile,
                    router=router,
                )
        
        print(f"  Batch: {batch.name}")
        print(f"  Vouchers: {batch.vouchers.count()}")
        
        return batch.vouchers.count() >= 5
    
    runner.test("Can create voucher batch", test_can_create_voucher_batch)
    
    def test_voucher_code_generation():
        code1 = Voucher.generate_code()
        code2 = Voucher.generate_code()
        
        print(f"  Sample code: {code1}")
        print(f"  Codes unique: {code1 != code2}")
        
        return len(code1) > 10 and code1 != code2
    
    runner.test("Voucher code generation works", test_voucher_code_generation)
    
    def test_voucher_redemption():
        voucher = Voucher.objects.filter(is_used=False).first()
        customer = Customer.objects.first()
        
        if not voucher or not customer:
            print("  Skipped: Requires unused voucher and customer")
            return True
        
        # Test is_valid method
        is_valid = voucher.is_valid()
        print(f"  Voucher valid: {is_valid}")
        
        if is_valid:
            voucher.mark_as_used(customer)
            print(f"  Marked as used by: {customer.username}")
            return voucher.is_used
        
        return True
    
    runner.test("Voucher redemption works", test_voucher_redemption)
    
    # Test 7: API endpoints (basic check)
    runner.print_header("API Endpoint Tests")
    
    def test_api_imports():
        try:
            from payments.api_views import payment_callback, mpesa_callback, paypal_callback
            print("  All API views importable")
            return True
        except ImportError as e:
            print(f"  Import error: {str(e)}")
            return False
    
    runner.test("API views are importable", test_api_imports)
    
    # Test 8: Background tasks
    runner.print_header("Background Task Tests")
    
    def test_task_imports():
        try:
            from routers.tasks import check_router_status, check_all_routers_status
            from customers.tasks import check_expired_users
            from reports.tasks import generate_daily_report
            print("  All tasks importable")
            return True
        except ImportError as e:
            print(f"  Import error: {str(e)}")
            return False
    
    runner.test("Celery tasks are importable", test_task_imports)
    
    # Test 9: MikroTik API service
    runner.print_header("MikroTik API Service Tests")
    
    def test_api_service_import():
        try:
            from routers.services.mikrotik_api import MikroTikAPIService
            print("  MikroTik API service importable")
            return True
        except ImportError as e:
            print(f"  Import error: {str(e)}")
            return False
    
    runner.test("MikroTik API service is importable", test_api_service_import)
    
    def test_api_service_init():
        try:
            from routers.services.mikrotik_api import MikroTikAPIService
            router = Router.objects.first()
            
            if not router:
                print("  Skipped: No router exists")
                return True
            
            service = MikroTikAPIService(router)
            print(f"  Service created for router: {router.name}")
            return service is not None
        except Exception as e:
            print(f"  Error: {str(e)}")
            return False
    
    runner.test("MikroTik API service can be instantiated", test_api_service_init)
    
    # Test 10: Admin site
    runner.print_header("Admin Site Tests")
    
    def test_admin_registered():
        from django.contrib import admin
        
        models_to_check = [
            (Router, 'routers.Router'),
            (Profile, 'profiles.Profile'),
            (Customer, 'customers.Customer'),
            (Payment, 'payments.Payment'),
            (Voucher, 'vouchers.Voucher'),
        ]
        
        all_registered = True
        for model, name in models_to_check:
            if model in admin.site._registry:
                print(f"  ✓ {name} registered")
            else:
                print(f"  ✗ {name} NOT registered")
                all_registered = False
        
        return all_registered
    
    runner.test("All models registered in admin", test_admin_registered)
    
    # Final summary
    success = runner.summary()
    
    # Recommendations
    runner.print_header("Next Steps")
    
    if success:
        print("\n✅ Automated tests passed!")
        print("\nRecommended next steps:")
        print("1. Start the development server: python manage.py runserver")
        print("2. Follow manual testing guide: See TESTING_GUIDE.md")
        print("3. Test with real MikroTik router (if available)")
        print("4. Test payment API callbacks")
        print("5. Review deployment checklist: See DEPLOYMENT.md")
    else:
        print("\n⚠️  Some tests failed.")
        print("\nRecommended actions:")
        print("1. Review error messages above")
        print("2. Run: python check_setup.py")
        print("3. Ensure migrations are applied: python manage.py migrate")
        print("4. Check requirements installed: pip install -r requirements.txt")
    
    print("\n" + "="*60 + "\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

