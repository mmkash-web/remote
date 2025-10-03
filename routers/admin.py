"""
Admin configuration for routers app.
"""
from django.contrib import admin
from .models import Router, RouterLog


@admin.register(Router)
class RouterAdmin(admin.ModelAdmin):
    list_display = ['name', 'vpn_ip', 'status', 'is_active', 'total_users', 'active_users', 'last_checked', 'created_at']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['name', 'vpn_ip', 'router_identity', 'description']
    readonly_fields = ['id', 'status', 'last_checked', 'last_online', 'created_at', 'updated_at', 
                       'router_model', 'router_version', 'router_identity', 'total_users', 'active_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'is_active')
        }),
        ('Connection Details', {
            'fields': ('vpn_ip', 'api_port', 'username', 'password')
        }),
        ('Status', {
            'fields': ('status', 'last_checked', 'last_online')
        }),
        ('Router Information', {
            'fields': ('router_model', 'router_version', 'router_identity')
        }),
        ('Statistics', {
            'fields': ('total_users', 'active_users')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RouterLog)
class RouterLogAdmin(admin.ModelAdmin):
    list_display = ['router', 'log_type', 'action', 'message', 'created_at', 'created_by']
    list_filter = ['log_type', 'router', 'created_at']
    search_fields = ['action', 'message', 'router__name']
    readonly_fields = ['router', 'log_type', 'action', 'message', 'details', 'created_at', 'created_by']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

