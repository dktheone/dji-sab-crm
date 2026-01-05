"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView # Import RedirectView
from apps.emp.views import (
    custom_login, 
    custom_logout, 
    dashboard,
    password_change,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

urlpatterns = [
    # path('logouts/', LogoutView.as_view(next_page='custom_login'), name='custom_logout'),
    path("", dashboard, name="dashboard"),  # root URL → dashboard
    path('dashboard/', dashboard, name='dashboard'),
    # path('', dashboard, name='dashboard'), 
    path('login/', custom_login, name='custom_login'),
    path('log_out/', custom_logout, name='custom_logout'),
    
    # Password Management URLs
    path('password-change/', password_change, name='password_change'),
    path('password-change/<int:employee_id>/', password_change, name='password_change_admin'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('emp/', include('apps.emp.urls', namespace='emp')),
    path('leads/', include('apps.leads.urls')),
    path('vendors/', include('apps.vendors.urls', namespace='vendors')),
    # path('', include('apps.dyn_dt.urls')),
    # path('', include('apps.dyn_api.urls')),
    path('charts/', include('apps.charts.urls')),
    path("admin/", admin.site.urls),
    # path("", include('admin_adminlte.urls')),
    path("select2/", include("django_select2.urls")),

    # re_path(r"^select2/", include("select2.urls")),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

