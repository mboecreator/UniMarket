from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, Message, ProductLike, ProductView

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'condition', 'status', 'created_at']
    list_filter = ['category', 'condition', 'status', 'created_at']
    search_fields = ['title', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'created_at']
    list_filter = ['created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'product', 'message_type', 'subject', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'subject']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__title']

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__title', 'ip_address']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer', 'buyer_name', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'buyer__username', 'buyer_name', 'buyer_email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'buyer', 'status', 'payment_status')
        }),
        ('Contact Information', {
            'fields': ('buyer_name', 'buyer_email', 'buyer_phone')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_notes')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'seller', 'quantity', 'price', 'total']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product__title', 'seller__username']
