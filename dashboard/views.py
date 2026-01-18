from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from products.models import Product, Category, Brand
from .models import Cart, CartItem, Banner
from user_management.models import Wishlist
from review_system.models import Review
import json


@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    User = get_user_model()
    total_products = Product.objects.count()
    total_users = User.objects.count()
    total_reviews = Review.objects.count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'recent_users': recent_users,
    }
    return render(request, 'admin_dashboard.html', context)


@ensure_csrf_cookie
def home(request):
    """Homepage view with featured products and banners"""
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True
    ).select_related('brand', 'category')[:8]
    
    bestseller_products = Product.objects.filter(
        is_bestseller=True, 
        is_active=True
    ).select_related('brand', 'category')[:6]
    
    new_arrivals = Product.objects.filter(
        is_new_arrival=True, 
        is_active=True
    ).select_related('brand', 'category')[:6]
    
    now = timezone.now()
    hero_banners = (
        Banner.objects.filter(
            banner_type='hero',
            is_active=True
        )
        .filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now),
        )
        .order_by('order')[:3]
    )
    
    categories = Category.objects.filter(is_active=True, parent=None)[:6]
    
    context = {
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'new_arrivals': new_arrivals,
        'hero_banners': hero_banners,
        'categories': categories,
    }
    
    return render(request, 'dashboard/home.html', context)


def about(request):
    """About page view"""
    return render(request, 'dashboard/about.html')


def contact(request):
    """Contact page view - handles both GET and POST requests"""
    if request.method == 'POST':
        # Process the contact form submission
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        newsletter = request.POST.get('newsletter', False)
        
        # Validate required fields
        if not all([first_name, last_name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'dashboard/contact.html')
        
        # Validate email format
        if '@' not in email or '.' not in email:
            messages.error(request, 'Please provide a valid email address.')
            return render(request, 'dashboard/contact.html')
        
        try:
            # Create and save contact message
            from .models import ContactMessage
            contact_msg = ContactMessage.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
                newsletter_subscribed=bool(newsletter)
            )
            
            # Show success message
            messages.success(request, 'Thank you! Your message has been sent successfully. We will get back to you soon.')
            
            # Log for debugging
            print(f"Contact message created: {contact_msg}")
            
            # Redirect to same page to avoid form resubmission
            return redirect('dashboard:contact')
            
        except Exception as e:
            print(f"Error saving contact message: {str(e)}")
            messages.error(request, 'An error occurred while sending your message. Please try again.')
            return render(request, 'dashboard/contact.html')
    
    # Handle GET request - just render the form
    return render(request, 'dashboard/contact.html')


def search_products(request):
    """
    Product search view using LINEAR SEARCH algorithm.
    
    This implementation performs a case-insensitive linear search by iterating
    through all products one by one and comparing the search keyword only with
    the product name. No database queries or full-text search is used.
    """
    query = request.GET.get('q', '').strip()
    
    # Fetch all active products from the database (one-time fetch)
    all_products = Product.objects.filter(is_active=True).select_related('brand', 'category')
    
    # Initialize list to store matched products
    matched_products = []
    
    if query:
        # LINEAR SEARCH: Loop through all products one by one
        # This algorithm checks each product name sequentially
        query_lower = query.lower()  # Convert search query to lowercase for case-insensitive comparison
        
        for product in all_products:
            # Compare the search keyword only with the product name (case-insensitive)
            if query_lower in product.name.lower():
                matched_products.append(product)
    else:
        # If no query is provided, show all products
        matched_products = list(all_products)
    
    # Get filter options
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'products': matched_products,
        'query': query,
        'categories': categories,
        'brands': brands,
        'total_results': len(matched_products),
    }
    
    return render(request, 'dashboard/search_results.html', context)


def product_suggestions(request):
    """
    API endpoint that returns product name suggestions using LINEAR SEARCH.
    
    This endpoint is called via AJAX when user types in the search bar.
    Returns JSON with matching product names (limited to 8 suggestions).
    
    Linear search algorithm: Check each product name sequentially for matches.
    """
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if query and len(query) >= 2:  # Only search if query has at least 2 characters
        # Fetch all active products from the database
        all_products = Product.objects.filter(is_active=True).values('name', 'slug')
        
        # Convert query to lowercase for case-insensitive comparison
        query_lower = query.lower()
        
        # LINEAR SEARCH: Loop through all products one by one
        # This algorithm checks each product name sequentially
        for product in all_products:
            # Compare the search keyword only with the product name (case-insensitive)
            if query_lower in product['name'].lower():
                suggestions.append({
                    'name': product['name'],
                    'slug': product['slug']
                })
                # Limit suggestions to 8 results
                if len(suggestions) >= 8:
                    break
    
    return JsonResponse({'suggestions': suggestions})


def cart_view(request):
    """Shopping cart view"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'dashboard/cart.html', context)


def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        # Treat fetch() requests as AJAX even if X-Requested-With is not set
        if (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or 'application/json' in (request.headers.get('Accept') or '')
        ):
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart.total_items
            })
        return redirect('dashboard:cart')

    # If not POST, force JSON error for AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    return redirect('dashboard:cart')


def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.user.is_authenticated:
        if cart_item.cart.user == request.user:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'{product_name} removed from cart!')
    else:
        if cart_item.cart.session_key == request.session.session_key:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'{product_name} removed from cart!')
    
    return redirect('dashboard:cart')


def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
    
    return redirect('dashboard:cart')


@login_required
def wishlist_view(request):
    """User wishlist view"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'dashboard/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
    
    return redirect('dashboard:wishlist')


@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f'{product.name} removed from wishlist!')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Product not found in wishlist!')
    
    return redirect('dashboard:wishlist')


def get_or_create_cart(request):
    """Helper function to get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )
    
    return cart


def custom_logout(request):
    """Simple custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully signed out.')
    return redirect('dashboard:home')
