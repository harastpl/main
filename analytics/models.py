from django.db import models
from django.contrib.auth.models import User
from core.models import Product


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    viewed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_on']

    def __str__(self):
        if self.user:
            return f"View of {self.product.name} by {self.user.username}"
        return f"View of {self.product.name} by Anonymous"


class CartAnalytics(models.Model):
    """Track cart abandonment and conversion metrics"""
    session_key = models.CharField(max_length=40, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    items_count = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    converted = models.BooleanField(default=False)  # True if cart led to order

    def __str__(self):
        user_info = self.user.username if self.user else f"Session: {self.session_key}"
        return f"Cart Analytics - {user_info} - {self.items_count} items"