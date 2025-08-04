from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    location = models.CharField(max_length=200, help_text="Where on campus to meet")
    
    # Seller contact information (optional - can override profile defaults)
    seller_phone = models.CharField(max_length=15, blank=True, help_text="Contact phone number for this product")
    seller_email = models.EmailField(blank=True, help_text="Contact email for this product (if different from account email)")
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('message', 'In-app Message'),
            ('any', 'Any Method')
        ],
        default='message',
        help_text="Preferred way for buyers to contact you"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
    
    def get_seller_contact_info(self):
        """Get seller contact information, falling back to profile defaults"""
        contact_info = {
            'phone': self.seller_phone or getattr(self.seller.userprofile, 'phone_number', ''),
            'email': self.seller_email or self.seller.email,
            'preferred_method': self.preferred_contact_method
        }
        return contact_info

    class Meta:
        ordering = ['-created_at']

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.title}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        from decimal import Decimal
        total = sum(item.get_total_price() for item in self.items.all())
        return Decimal(str(total)) if total else Decimal('0.00')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_total_price(self):
        from decimal import Decimal
        return Decimal(str(self.quantity)) * self.product.price

    class Meta:
        unique_together = ['cart', 'product']

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_total_price(self):
        return self.quantity * self.price

class Message(models.Model):
    MESSAGE_TYPES = [
        ('inquiry', 'Product Inquiry'),
        ('offer', 'Price Offer'),
        ('general', 'General Message'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='inquiry')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    
    # Optional fields for offers
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # For reply threading
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} about {self.product.title if self.product else 'General'}"

    class Meta:
        ordering = ['-created_at']

class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} likes {self.product.title}"

    class Meta:
        unique_together = ['user', 'product']

class ProductView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_views', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View of {self.product.title} by {self.user.username if self.user else self.ip_address}"

    class Meta:
        ordering = ['-created_at']

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Order details
    order_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Contact information
    buyer_name = models.CharField(max_length=100, null=True, blank=True)
    buyer_email = models.EmailField(null=True, blank=True)
    buyer_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Delivery information
    delivery_address = models.TextField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True)
    
    # Order status
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', null=True, blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number} by {self.buyer.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_items', null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # quantity * price
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title} in Order {self.order.order_number if self.order.order_number else self.order.id}"
