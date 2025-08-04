from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    university = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Seller subscription fields
    is_seller = models.BooleanField(default=False)
    subscription_active = models.BooleanField(default=False)
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.student_id or 'No Student ID'}"

    def is_subscription_active(self):
        """Check if user has an active seller subscription"""
        if not self.subscription_active:
            return False
        
        # Check if subscription has expired
        if self.subscription_end_date and self.subscription_end_date < timezone.now():
            try:
                self.subscription_active = False
                self.save(update_fields=['subscription_active'])
            except Exception as e:
                # Log error but don't break the flow
                print(f"Error updating subscription status: {e}")
            return False
        return True

    def can_post_products(self):
        """Check if user can post products (has active subscription)"""
        return self.is_seller and self.is_subscription_active()

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class SellerSubscription(models.Model):
    SUBSCRIPTION_TYPES = [
        ('monthly', 'Monthly - $10'),
        ('quarterly', 'Quarterly - $25'),
        ('yearly', 'Yearly - $90'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type} ({self.payment_status})"

    def save(self, *args, **kwargs):
        # Set amount based on subscription type
        if self.subscription_type == 'monthly':
            self.amount = 10.00
        elif self.subscription_type == 'quarterly':
            self.amount = 25.00
        elif self.subscription_type == 'yearly':
            self.amount = 90.00
        
        # Set end date based on subscription type and start date
        if self.start_date:
            if self.subscription_type == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            elif self.subscription_type == 'quarterly':
                self.end_date = self.start_date + timedelta(days=90)
            elif self.subscription_type == 'yearly':
                self.end_date = self.start_date + timedelta(days=365)
        
        super().save(*args, **kwargs)
        
        # Update user profile subscription status
        if self.payment_status == 'completed':
            profile, created = UserProfile.objects.get_or_create(user=self.user)
            profile.is_seller = True
            profile.subscription_active = True
            profile.subscription_start_date = self.start_date
            profile.subscription_end_date = self.end_date
            profile.save()

    class Meta:
        ordering = ['-created_at']
