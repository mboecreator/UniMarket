#!/usr/bin/env python3
"""
Create Demo Seller Account
This script creates a demo seller account with active subscription for testing.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append('/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_market_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile, SellerSubscription
from products.models import Product, Category

def create_demo_seller():
    """Create a demo seller account with active subscription"""
    print("🔧 Creating Demo Seller Account")
    print("=" * 40)
    
    # Clean up existing demo user
    try:
        user = User.objects.get(username='demoseller')
        user.delete()
        print("🧹 Cleaned up existing demo seller")
    except User.DoesNotExist:
        pass
    
    # Create user
    user = User.objects.create_user(
        username='demoseller',
        email='demoseller@university.edu',
        password='demo123',
        first_name='Demo',
        last_name='Seller'
    )
    
    # Create profile with active subscription
    profile = UserProfile.objects.create(
        user=user,
        student_id='DEMO123',
        university='Demo University',
        phone_number='555-0123',
        address='123 Campus Drive',
        is_seller=True,
        subscription_active=True,
        subscription_start_date=timezone.now(),
        subscription_end_date=timezone.now() + timedelta(days=30)
    )
    
    # Create subscription record
    subscription = SellerSubscription.objects.create(
        user=user,
        subscription_type='monthly',
        amount=10.00,
        payment_status='completed',
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30)
    )
    
    print(f"✅ Demo seller created successfully!")
    print(f"   Username: {user.username}")
    print(f"   Password: demo123")
    print(f"   Email: {user.email}")
    print(f"   Can post products: {profile.can_post_products()}")
    print(f"   Subscription active: {profile.is_subscription_active()}")
    
    return user, profile

def create_demo_products(user):
    """Create some demo products for the seller"""
    print("\n🛍️ Creating Demo Products")
    print("=" * 40)
    
    # Get or create categories
    categories = Category.objects.all()
    if not categories.exists():
        print("No categories found. Please create some categories first.")
        return []
    
    demo_products_data = [
        {
            'title': 'MacBook Pro 13" (2021)',
            'description': 'Excellent condition MacBook Pro with M1 chip. Perfect for students. Includes charger and original box.',
            'price': 899.99,
            'condition': 'like_new',
            'location': 'Library Starbucks'
        },
        {
            'title': 'Calculus Textbook - Stewart 8th Edition',
            'description': 'Used calculus textbook in good condition. Some highlighting but all pages intact.',
            'price': 45.00,
            'condition': 'good',
            'location': 'Math Building Lobby'
        },
        {
            'title': 'Dorm Room Mini Fridge',
            'description': 'Compact refrigerator perfect for dorm rooms. Clean and working perfectly.',
            'price': 75.00,
            'condition': 'good',
            'location': 'Student Union'
        }
    ]
    
    products = []
    for i, product_data in enumerate(demo_products_data):
        try:
            # Use appropriate category
            if 'MacBook' in product_data['title']:
                category = categories.filter(name__icontains='Electronics').first() or categories.first()
            elif 'Textbook' in product_data['title']:
                category = categories.filter(name__icontains='Textbook').first() or categories.first()
            else:
                category = categories.filter(name__icontains='Furniture').first() or categories.first()
            
            product = Product.objects.create(
                seller=user,
                title=product_data['title'],
                description=product_data['description'],
                category=category,
                price=product_data['price'],
                condition=product_data['condition'],
                location=product_data['location'],
                seller_phone='555-0123',
                seller_email=user.email,
                preferred_contact_method='message'
            )
            
            products.append(product)
            print(f"✅ Created: {product.title} - ${product.price}")
            
        except Exception as e:
            print(f"❌ Failed to create product {i+1}: {e}")
    
    print(f"\n📊 Created {len(products)} demo products")
    return products

def show_access_info():
    """Show how to access the seller features"""
    print("\n🚀 How to Access Seller Features")
    print("=" * 40)
    print("1. Login with demo seller account:")
    print("   - Username: demoseller")
    print("   - Password: demo123")
    print("   - URL: http://127.0.0.1:8000/accounts/login/")
    print("")
    print("2. Choose 'Seller' when logging in")
    print("")
    print("3. Access seller features:")
    print("   - Seller Dashboard: http://127.0.0.1:8000/accounts/seller/dashboard/")
    print("   - Add Product: http://127.0.0.1:8000/add-product/")
    print("   - My Products: http://127.0.0.1:8000/my-products/")
    print("")
    print("4. Or use the navigation menu:")
    print("   - Click on your profile avatar")
    print("   - Select 'Seller Dashboard'")
    print("   - Select 'Add Product'")
    print("   - Select 'My Products'")

def main():
    """Create demo seller and show access information"""
    print("🎭 Demo Seller Account Creator")
    print("=" * 50)
    
    try:
        # Create demo seller
        user, profile = create_demo_seller()
        
        # Create demo products
        products = create_demo_products(user)
        
        # Show access information
        show_access_info()
        
        print("\n" + "=" * 50)
        print("🎉 Demo seller account created successfully!")
        print("You can now test the seller product management system.")
        
    except Exception as e:
        print(f"\n❌ Failed to create demo seller: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()