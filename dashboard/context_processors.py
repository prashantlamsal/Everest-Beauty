from .models import Cart
from user_management.models import Wishlist


def cart_and_wishlist_counts(request):
    """Provide navbar counts for cart and wishlist."""
    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user).first()
    else:
        if not request.session.session_key:
            request.session.create()
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if cart:
        cart_count = cart.total_items

    return {
        'navbar_cart_count': cart_count,
        'navbar_wishlist_count': wishlist_count,
    }
