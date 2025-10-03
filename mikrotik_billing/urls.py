"""
URL configuration for MikroTik Billing Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Main application URLs
    path('', include('dashboard.urls')),
    path('routers/', include('routers.urls')),
    path('customers/', include('customers.urls')),
    path('profiles/', include('profiles.urls')),
    path('payments/', include('payments.urls')),
    path('vouchers/', include('vouchers.urls')),
    path('reports/', include('reports.urls')),
    
    # API endpoints
    path('api/', include('payments.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "MikroTik Billing Admin"
admin.site.site_title = "MikroTik Billing"
admin.site.index_title = "Welcome to MikroTik Billing Management"

