"""
Admin configuration for reports app.
"""
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'start_date', 'end_date', 'generated_at', 'generated_by']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['title', 'summary']
    readonly_fields = ['id', 'data', 'generated_at']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'report_type', 'title')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Report Data', {
            'fields': ('data', 'summary'),
            'classes': ('collapse',)
        }),
        ('Generation Info', {
            'fields': ('generated_at', 'generated_by')
        }),
    )

