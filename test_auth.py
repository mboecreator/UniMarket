#!/usr/bin/env python3
"""
Test Authentication System
This script tests the new authentication system functionality.
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Add the project directory to Python path
sys.path.append('/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_market_backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def test_authentication_pages():
    """Test that authentication pages load correctly"""
    client = Client()
    
    print("🔍 Testing Authentication Pages")
    print("=" * 40)
    
    # Test login page
    response = client.get('/accounts/login/')
    if response.status_code == 200:
        print("✅ Login page: OK")
    else:
        print(f"❌ Login page: FAILED (Status: {response.status_code})")
    
    # Test register page
    response = client.get('/accounts/register/')
    if response.status_code == 200:
        print("✅ Register page: OK")
    else:
        print(f"❌ Register page: FAILED (Status: {response.status_code})")
    
    return True

def test_user_registration():
    """Test user registration functionality"""
    client = Client()
    
    print("\n🔍 Testing User Registration")
    print("=" * 40)
    
    # Test buyer registration
    buyer_data = {
        'username': 'testbuyer123',
        'email': 'testbuyer@university.edu',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'user_type': 'buyer'
    }
    
    response = client.post('/accounts/register/', buyer_data)
    if response.status_code == 302:  # Redirect after successful registration
        print("✅ Buyer registration: OK")
        
        # Check if user was created
        if User.objects.filter(username='testbuyer123').exists():
            print("✅ Buyer user created: OK")
            
            # Check if profile was created
            user = User.objects.get(username='testbuyer123')
            if UserProfile.objects.filter(user=user).exists():
                print("✅ Buyer profile created: OK")
            else:
                print("❌ Buyer profile creation: FAILED")
        else:
            print("❌ Buyer user creation: FAILED")
    else:
        print(f"❌ Buyer registration: FAILED (Status: {response.status_code})")
    
    # Test seller registration
    seller_data = {
        'username': 'testseller123',
        'email': 'testseller@university.edu',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'user_type': 'seller'
    }
    
    response = client.post('/accounts/register/', seller_data)
    if response.status_code == 302:  # Redirect after successful registration
        print("✅ Seller registration: OK")
        
        # Check if user was created
        if User.objects.filter(username='testseller123').exists():
            print("✅ Seller user created: OK")
            
            # Check if profile was created
            user = User.objects.get(username='testseller123')
            if UserProfile.objects.filter(user=user).exists():
                print("✅ Seller profile created: OK")
            else:
                print("❌ Seller profile creation: FAILED")
        else:
            print("❌ Seller user creation: FAILED")
    else:
        print(f"❌ Seller registration: FAILED (Status: {response.status_code})")
    
    return True

def test_user_login():
    """Test user login functionality"""
    client = Client()
    
    print("\n🔍 Testing User Login")
    print("=" * 40)
    
    # Create a test user first
    test_user = User.objects.create_user(
        username='logintest',
        email='logintest@university.edu',
        password='testpass123'
    )
    UserProfile.objects.create(user=test_user)
    
    # Test buyer login
    buyer_login_data = {
        'username': 'logintest',
        'password': 'testpass123',
        'user_type': 'buyer'
    }
    
    response = client.post('/accounts/login/', buyer_login_data)
    if response.status_code == 302:  # Redirect after successful login
        print("✅ Buyer login: OK")
    else:
        print(f"❌ Buyer login: FAILED (Status: {response.status_code})")
    
    # Test seller login
    seller_login_data = {
        'username': 'logintest',
        'password': 'testpass123',
        'user_type': 'seller'
    }
    
    response = client.post('/accounts/login/', seller_login_data)
    if response.status_code == 302:  # Redirect after successful login
        print("✅ Seller login: OK")
    else:
        print(f"❌ Seller login: FAILED (Status: {response.status_code})")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    # Delete test users
    test_usernames = ['testbuyer123', 'testseller123', 'logintest']
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"✅ Deleted user: {username}")
        except User.DoesNotExist:
            pass

def main():
    """Run all authentication tests"""
    print("🧪 Authentication System Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        test_authentication_pages()
        test_user_registration()
        test_user_login()
        
        print("\n" + "=" * 50)
        print("🎉 All authentication tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    finally:
        # Clean up
        cleanup_test_data()
        print("\n✨ Test cleanup completed.")

if __name__ == "__main__":
    main()