"""
Admin configuration for profiles app.
"""
from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_speed_display', 'price', 'currency', 
                    'get_duration_display_text', 'is_active', 'is_public', 'total_customers']
    list_filter = ['is_active', 'is_public', 'duration_unit', 'currency']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_customers', 'rate_limit']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description')
        }),
        ('Bandwidth Settings', {
            'fields': ('download_speed', 'upload_speed', 'rate_limit', 'data_limit_mb')
        }),
        ('Duration & Pricing', {
            'fields': ('duration_value', 'duration_unit', 'price', 'currency')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_public')
        }),
        ('Statistics', {
            'fields': ('total_customers',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

