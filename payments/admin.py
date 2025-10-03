"""
Admin configuration for payments app.
"""
from django.contrib import admin
from .models import Payment, PaymentGatewayLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'customer', 'amount', 'currency', 
                    'payment_method', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['transaction_id', 'reference_code', 'customer__username', 
                     'customer__full_name']
    readonly_fields = ['id', 'created_at', 'completed_at', 'gateway_response']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('id', 'customer', 'profile', 'amount', 'currency')
        }),
        ('Transaction Details', {
            'fields': ('payment_method', 'status', 'transaction_id', 'reference_code')
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processed_by', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        for payment in queryset:
            if payment.status != 'COMPLETED':
                payment.processed_by = request.user
                payment.mark_completed()
        self.message_user(request, f"{queryset.count()} payments marked as completed.")
    mark_as_completed.short_description = "Mark selected payments as completed"
    
    def mark_as_failed(self, request, queryset):
        for payment in queryset:
            payment.mark_failed("Marked as failed by admin")
        self.message_user(request, f"{queryset.count()} payments marked as failed.")
    mark_as_failed.short_description = "Mark selected payments as failed"


@admin.register(PaymentGatewayLog)
class PaymentGatewayLogAdmin(admin.ModelAdmin):
    list_display = ['gateway', 'log_type', 'payment', 'status_code', 'message', 'created_at']
    list_filter = ['gateway', 'log_type', 'created_at']
    search_fields = ['message', 'gateway']
    readonly_fields = ['payment', 'log_type', 'gateway', 'request_data', 
                       'response_data', 'status_code', 'message', 'created_at', 'ip_address']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('payment', 'gateway', 'log_type', 'status_code')
        }),
        ('Request Data', {
            'fields': ('request_data',),
            'classes': ('collapse',)
        }),
        ('Response Data', {
            'fields': ('response_data',),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('message', 'ip_address', 'created_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

