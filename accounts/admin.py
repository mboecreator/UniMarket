from django.contrib import admin
from .models import UserProfile, SellerSubscription

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'university', 'is_seller', 'subscription_active']
    list_filter = ['is_seller', 'subscription_active', 'university']
    search_fields = ['user__username', 'student_id', 'university']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SellerSubscription)
class SellerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_type', 'amount', 'payment_status', 'start_date', 'end_date']
    list_filter = ['subscription_type', 'payment_status']
    search_fields = ['user__username', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
