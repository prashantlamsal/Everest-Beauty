from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from products.models import Product, Category, Brand
from .models import Cart, CartItem
from user_management.models import Wishlist
from .serializers import (
    ProductSerializer, CategorySerializer, BrandSerializer,
    CartSerializer, CartItemSerializer, WishlistSerializer
)


class ProductListAPI(generics.ListAPIView):
    """API view for listing products with filtering"""
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category')
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'brand', 'product_type', 'is_featured', 'is_bestseller']
    search_fields = ['name', 'description', 'brand__name', 'category__name']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']


class ProductDetailAPI(generics.RetrieveAPIView):
    """API view for product detail"""
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category')
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class CategoryListAPI(generics.ListAPIView):
    """API view for listing categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class BrandListAPI(generics.ListAPIView):
    """API view for listing brands"""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer


class CartAPI(generics.RetrieveAPIView):
    """API view for cart operations"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartAPI(generics.CreateAPIView):
    """API view for adding items to cart"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {'error': 'Product ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveFromCartAPI(generics.DestroyAPIView):
    """API view for removing items from cart"""
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        
        if cart_item.cart.user != request.user:
            return Response(
                {'error': 'Not authorized'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        cart_item.delete()
        
        cart = request.user.carts.first()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateCartItemAPI(generics.UpdateAPIView):
    """API view for updating cart item quantity"""
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    
    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        
        if cart_item.cart.user != request.user:
            return Response(
                {'error': 'Not authorized'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = request.user.carts.first()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WishlistAPI(generics.ListAPIView):
    """API view for user wishlist"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')


class AddToWishlistAPI(generics.CreateAPIView):
    """API view for adding products to wishlist"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            message = f'{product.name} added to wishlist!'
        else:
            message = f'{product.name} is already in your wishlist!'
        
        return Response({'message': message}, status=status.HTTP_200_OK)


class RemoveFromWishlistAPI(generics.DestroyAPIView):
    """API view for removing products from wishlist"""
    permission_classes = [IsAuthenticated]
    queryset = Wishlist.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user, 
                product_id=product_id
            )
            product_name = wishlist_item.product.name
            wishlist_item.delete()
            
            return Response(
                {'message': f'{product_name} removed from wishlist!'}, 
                status=status.HTTP_200_OK
            )
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Product not found in wishlist!'}, 
                status=status.HTTP_404_NOT_FOUND
            )
