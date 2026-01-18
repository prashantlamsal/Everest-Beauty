from django.contrib import admin
from .models import Cart, CartItem, Banner, ContactMessage


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price', 'added_at']
    fields = ['product', 'quantity', 'total_price', 'added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'total_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'session_key')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'banner_type', 'is_active', 'order', 'start_date', 'end_date'
    ]
    list_filter = ['banner_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Banner Information', {
            'fields': ('title', 'subtitle', 'image', 'banner_type', 'link_url')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name', 'email', 'get_subject_display', 'is_read', 'created_at'
    ]
    list_filter = ['subject', 'is_read', 'newsletter_subscribed', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Sender Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Settings', {
            'fields': ('is_read', 'newsletter_subscribed')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Name'