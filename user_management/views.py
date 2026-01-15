from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile, Wishlist
from order_management.models import Order, ShippingAddress

@login_required
def user_profile(request):
    """Display user profile"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'user_management/user_profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        
        # Update profile fields
        profile.phone = request.POST.get('phone', '').strip()
        profile.gender = request.POST.get('gender', '')
        profile.skin_type = request.POST.get('skin_type', '').strip()
        profile.skin_concerns = request.POST.get('skin_concerns', '').strip()
        
        # Handle date of birth
        dob = request.POST.get('date_of_birth', '').strip()
        if dob:
            from datetime import datetime
            try:
                profile.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_management:user_profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'user_management/edit_profile.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user_management:user_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'user_management/change_password.html', context)


@login_required
def user_settings(request):
    """Account settings: email, notifications, privacy"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            request.user.email = email
            request.user.save()

        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.privacy_mode = request.POST.get('privacy_mode') == 'on'
        profile.save()

        messages.success(request, 'Settings updated successfully.')
        return redirect('user_management:user_settings')

    context = {
        'profile': profile,
    }
    return render(request, 'user_management/user_settings.html', context)

@login_required
def user_orders(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'user_management/user_orders.html', context)

@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow cancellation for pending, confirmed, or processing orders
    if order.status in ['pending', 'confirmed', 'processing']:
        if request.method == 'POST':
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Order #{order.order_number} has been cancelled successfully.')
        else:
            messages.error(request, 'Invalid request method.')
    else:
        messages.error(request, f'Order #{order.order_number} cannot be cancelled (current status: {order.get_status_display()}).')
    
    return redirect('user_management:user_orders')

@login_required
def user_wishlist(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'user_management/user_wishlist.html', context)

@login_required
def user_addresses(request):
    """Manage user addresses"""
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'user_management/user_addresses.html', context)

@login_required
def add_address(request):
    """Add new shipping address"""
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
            ShippingAddress.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                is_default=is_default
            )
            messages.success(request, 'Address added successfully!')
            return redirect('user_management:user_addresses')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'user_management/add_address.html')

@login_required
def edit_address(request, address_id):
    """Edit shipping address"""
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
            return redirect('user_management:user_addresses')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'address': address,
    }
    return render(request, 'user_management/edit_address.html', context)

@login_required
def delete_address(request, address_id):
    """Delete shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('user_management:user_addresses')
    
    context = {
        'address': address,
    }
    return render(request, 'user_management/delete_address.html', context)

@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    from products.models import Product
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f'{product.name} removed from wishlist!')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Product not found in wishlist!')
    
    return redirect('user_management:user_wishlist')
