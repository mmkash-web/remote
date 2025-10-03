"""
Admin configuration for customers app.
"""
from django.contrib import admin
from .models import Customer, CustomerSession


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'router', 'profile', 'status', 
                    'is_active', 'expires_at', 'created_at']
    list_filter = ['status', 'is_active', 'router', 'profile', 'created_at']
    search_fields = ['username', 'full_name', 'email', 'phone_number']
    readonly_fields = ['id', 'created_at', 'activated_at', 'last_connection', 
                       'total_connections', 'data_used_mb', 'total_paid']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'username', 'password', 'full_name', 'email', 'phone_number')
        }),
        ('Assignment', {
            'fields': ('router', 'profile')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'created_at', 'activated_at', 'expires_at')
        }),
        ('Connection Tracking', {
            'fields': ('last_connection', 'total_connections', 'data_used_mb')
        }),
        ('Financial', {
            'fields': ('total_paid', 'outstanding_balance', 'last_payment_date')
        }),
        ('Settings', {
            'fields': ('auto_renewal', 'send_notifications', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by',)
        }),
    )
    
    actions = ['enable_customers', 'disable_customers']
    
    def enable_customers(self, request, queryset):
        count = queryset.update(is_active=True, status='ACTIVE')
        self.message_user(request, f"{count} customers enabled successfully.")
    enable_customers.short_description = "Enable selected customers"
    
    def disable_customers(self, request, queryset):
        count = queryset.update(is_active=False, status='DISABLED')
        self.message_user(request, f"{count} customers disabled successfully.")
    disable_customers.short_description = "Disable selected customers"


@admin.register(CustomerSession)
class CustomerSessionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'router', 'started_at', 'ended_at', 
                    'duration_seconds', 'ip_address']
    list_filter = ['router', 'started_at']
    search_fields = ['customer__username', 'ip_address', 'caller_id']
    readonly_fields = ['customer', 'router', 'started_at', 'ended_at', 
                       'duration_seconds', 'ip_address', 'caller_id', 
                       'bytes_in', 'bytes_out']
    date_hierarchy = 'started_at'
    
    def has_add_permission(self, request):
        return False

