"""
URL configuration for volt3dge project.

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
from core import views, order_views
from analytics.admin import analytics_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analytics-admin/', analytics_admin.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.product_list, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('cart/', include('cart.urls')),
    path('order/create/', order_views.order_create, name='order_create'),
    path('order/<int:order_id>/', order_views.order_detail, name='order_detail'),
    path('stl/', include('stl_uploads.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])