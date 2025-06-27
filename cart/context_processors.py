from .utils import get_or_create_cart


def cart(request):
    """Make cart available in all templates"""
    try:
        cart = get_or_create_cart(request)
        return {'cart': cart}
    except Exception:
        return {'cart': None}