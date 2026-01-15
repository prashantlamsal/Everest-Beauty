from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('settings/', views.user_settings, name='user_settings'),
    path('orders/', views.user_orders, name='user_orders'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('wishlist/', views.user_wishlist, name='user_wishlist'),
    path('addresses/', views.user_addresses, name='user_addresses'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
