from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum
from django.utils.html import format_html
from .models import ProductView, CartAnalytics
from core.models import Product
from cart.models import Cart, CartItem


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'session_key', 'ip_address', 'viewed_on']
    list_filter = ['viewed_on', 'product']
    search_fields = ['product__name', 'user__username']
    readonly_fields = ['viewed_on']


@admin.register(CartAnalytics)
class CartAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'items_count', 'total_value', 'converted', 'updated_at']
    list_filter = ['converted', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


class AnalyticsAdminSite(admin.AdminSite):
    site_header = "Volt3dge Analytics Dashboard"
    site_title = "Analytics"
    index_title = "Business Intelligence Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='analytics_dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Product view analytics
        product_views = ProductView.objects.select_related('product').values(
            'product__name'
        ).annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:10]

        # Cart analytics
        active_carts = Cart.objects.filter(
            cartitem__isnull=False
        ).distinct().count()

        # Products in carts
        products_in_carts = CartItem.objects.select_related('product').values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            cart_count=Count('cart', distinct=True)
        ).order_by('-total_quantity')[:10]

        # User cart details
        user_carts = Cart.objects.select_related('user').prefetch_related(
            'cartitem_set__product'
        ).filter(cartitem__isnull=False).distinct()[:20]

        # Recent product views
        recent_views = ProductView.objects.select_related(
            'product', 'user'
        ).order_by('-viewed_on')[:20]

        context = {
            'title': 'Analytics Dashboard',
            'product_views': product_views,
            'active_carts': active_carts,
            'products_in_carts': products_in_carts,
            'user_carts': user_carts,
            'recent_views': recent_views,
        }
        return render(request, 'admin/analytics_dashboard.html', context)

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = 'admin:analytics_dashboard'
        return super().index(request, extra_context)


# Create analytics admin site instance
analytics_admin = AnalyticsAdminSite(name='analytics_admin')

# Register models with analytics admin
analytics_admin.register(ProductView, ProductViewAdmin)
analytics_admin.register(CartAnalytics, CartAnalyticsAdmin)