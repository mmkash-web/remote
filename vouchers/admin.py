"""
Admin configuration for vouchers app.
"""
from django.contrib import admin
from .models import Voucher, VoucherBatch


@admin.register(VoucherBatch)
class VoucherBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile', 'router', 'quantity', 'price_per_voucher', 
                    'created_at', 'created_by']
    list_filter = ['profile', 'router', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description')
        }),
        ('Configuration', {
            'fields': ('profile', 'router', 'quantity', 'price_per_voucher')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at')
        }),
    )


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['code', 'batch', 'profile', 'is_used', 'is_active', 
                    'used_by', 'used_at', 'created_at']
    list_filter = ['is_used', 'is_active', 'profile', 'router', 'created_at']
    search_fields = ['code', 'used_by__username']
    readonly_fields = ['id', 'created_at', 'used_at', 'used_ip']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'code', 'batch', 'profile', 'router')
        }),
        ('Status', {
            'fields': ('is_active', 'is_used', 'expires_at')
        }),
        ('Usage Tracking', {
            'fields': ('used_by', 'used_at', 'used_ip')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['activate_vouchers', 'deactivate_vouchers']
    
    def activate_vouchers(self, request, queryset):
        count = queryset.filter(is_used=False).update(is_active=True)
        self.message_user(request, f"{count} vouchers activated.")
    activate_vouchers.short_description = "Activate selected vouchers"
    
    def deactivate_vouchers(self, request, queryset):
        count = queryset.filter(is_used=False).update(is_active=False)
        self.message_user(request, f"{count} vouchers deactivated.")
    deactivate_vouchers.short_description = "Deactivate selected vouchers"

