from django.utils.deprecation import MiddlewareMixin
from .models import ProductView


class ProductViewMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Track product detail views
        if view_func.__name__ == 'product_detail' and 'pk' in view_kwargs:
            try:
                from core.models import Product
                product = Product.objects.get(pk=view_kwargs['pk'])
                
                # Get client IP
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')

                # Create session if it doesn't exist
                if not request.session.session_key:
                    request.session.create()

                ProductView.objects.create(
                    product=product,
                    user=request.user if request.user.is_authenticated else None,
                    session_key=request.session.session_key,
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception:
                pass  # Silently fail to avoid breaking the request
        
        return None