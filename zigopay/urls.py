"""
URL configuration for zigopay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/', include('apps.authentication.urls')),
    
    # API Endpoints
    path('api/organizations/', include('apps.organizations.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/warehouses/', include('apps.warehouses.urls')),
    path('api/cargo/', include('apps.cargo.urls')),
    path('api/invoices/', include('apps.invoices.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    
    # WhatsApp Bot
    path('api/whatsapp/', include('apps.whatsapp.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
