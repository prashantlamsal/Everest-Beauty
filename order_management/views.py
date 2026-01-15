from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import Order, OrderItem, ShippingAddress
from .utils import send_order_confirmation_email
from dashboard.models import Cart
from payment_gateway.models import Payment
from django.utils import timezone
from datetime import timedelta

@login_required
def checkout(request):
    """Handle checkout process"""
    # Get fresh cart data from database
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.is_empty:
        messages.warning(request, 'Your cart is empty.')
        return redirect('dashboard:cart')
    
    if request.method == 'POST':
        # Create order from cart
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        province = request.POST.get('province', '').strip()
        delivery_method = request.POST.get('delivery_method', 'standard')
        payment_method = request.POST.get('payment_method', 'khalti')

        print(f"Checkout POST data: first_name={first_name}, last_name={last_name}, phone={phone}, address={address}, city={city}, province={province}, delivery_method={delivery_method}, payment_method={payment_method}")

        if not (first_name and last_name and phone and address and city and province):
            print(f"Missing required fields!")
            return JsonResponse({'success': False, 'message': 'Please fill all required fields.'}, status=400)

        # Compute delivery fee
        subtotal = float(cart.total_amount) if hasattr(cart, 'total_amount') else 0
        delivery_fee = 0
        if delivery_method == 'express':
            delivery_fee = 200
        elif delivery_method == 'standard':
            delivery_fee = 0 if subtotal >= 1000 else 100

        order_total = subtotal + delivery_fee
        
        print(f"Order totals: subtotal={subtotal}, delivery_fee={delivery_fee}, order_total={order_total}")

        from .models import Order, OrderItem
        try:
            order = Order.objects.create(
                user=request.user,
                status='pending',
                total_amount=order_total,
                shipping_address=f"{first_name} {last_name}\n{address}\n{city}, {province} {postal_code}",
                shipping_phone=phone,
                shipping_email=request.user.email,
                payment_method=payment_method,
                payment_status='pending',
            )
            
            print(f"Order created: {order.id}")

            # Create order items with current quantities from database
            for item in cart.items.select_related('product').all():
                print(f"Creating order item: {item.product.name} x {item.quantity}")
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name,
                    product_sku=item.product.sku,
                    quantity=item.quantity,
                    unit_price=item.product.current_price,
                    total_price=item.total_price,
                )

            # Clear cart
            cart.items.all().delete()
            print(f"Cart cleared")

            # Send confirmation email; failures must not block checkout
            try:
                est_date = None
                if delivery_method == 'express':
                    est_date = (timezone.localdate() + timedelta(days=2)).strftime('%b %d, %Y')
                elif delivery_method == 'standard':
                    est_date = (timezone.localdate() + timedelta(days=4)).strftime('%b %d, %Y')
                send_order_confirmation_email(order, request=request, estimated_delivery=est_date)
            except Exception as exc:
                print(f"Email send failed: {exc}")
                # continue without raising

            return JsonResponse({'success': True, 'order_id': order.id})
        except Exception as exc:
            print(f"Error creating order: {str(exc)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(exc)}, status=400)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'shipping_addresses': ShippingAddress.objects.filter(user=request.user),
        'KHALTI_PUBLIC_KEY': settings.KHALTI_PUBLIC_KEY,
    }
    return render(request, 'order_management/checkout.html', context)

@login_required
def order_detail(request, order_id):
    """Display order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'order_management/order_detail.html', context)

@login_required
def order_list(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'order_management/order_list.html', context)

@login_required
def order_tracking(request, order_id):
    """Display order tracking information"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'order_management/order_tracking.html', context)

@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'Order cannot be cancelled at this stage.')
    
    return redirect('order_management:order_detail', order_id=order_id)

@login_required
def shipping_address(request):
    """Manage shipping addresses"""
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'order_management/shipping_address.html', context)

@login_required
def edit_shipping_address(request, address_id):
    """Edit a shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_line1 = request.POST.get('address_line1', '').strip()
        address_line2 = request.POST.get('address_line2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', 'Nepal').strip()
        is_default = request.POST.get('is_default') == 'on'
        
        if full_name and phone and address_line1 and city and state:
            address.full_name = full_name
            address.phone = phone
            address.address_line1 = address_line1
            address.address_line2 = address_line2
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.country = country
            address.is_default = is_default
            address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('order_management:shipping_address')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'address': address,
    }
    return render(request, 'order_management/edit_shipping_address.html', context)
