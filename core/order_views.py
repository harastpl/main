from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.utils import get_or_create_cart
from .utils import send_order_to_google_sheets


def order_create(request):
    cart = get_or_create_cart(request)
    
    if not cart.cartitem_set.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total = cart.total_price
            order.save()
            
            # Create order items
            for cart_item in cart.cartitem_set.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity
                )
            
            # Clear the cart
            cart.clear()
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
            # Send to Google Sheets
            try:
                send_order_to_google_sheets(order)
            except Exception as e:
                print(f"Failed to send to Google Sheets: {e}")
            
            messages.success(request, f'Your order #{order.id} has been placed successfully!')
            return render(request, 'core/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()
    
    return render(request, 'core/order_create.html', {
        'cart': cart,
        'form': form
    })


def send_order_confirmation_email(order):
    """Send order confirmation email to customer and admin"""
    subject = f'Order #{order.id} Confirmation - Volt3dge'
    
    # Customer email
    customer_message = render_to_string('emails/order_confirmation.html', {'order': order})
    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=customer_message,
        fail_silently=True
    )
    
    # Admin notification
    admin_subject = f'New Order #{order.id} - Volt3dge'
    admin_message = render_to_string('emails/admin_order_notification.html', {'order': order})
    send_mail(
        admin_subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        html_message=admin_message,
        fail_silently=True
    )


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Only allow order owner or staff to view
    if not request.user.is_staff and order.user != request.user:
        messages.error(request, 'You can only view your own orders.')
        return redirect('home')
    
    return render(request, 'core/order_detail.html', {'order': order})