#!/usr/bin/env python3
"""
Test Seller Pages Styling
Quick test to verify the seller pages are loading with proper styling.
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Add the project directory to Python path
sys.path.append('/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_market_backend.settings')
django.setup()

def test_seller_pages():
    """Test that seller pages load correctly with styling"""
    print("🧪 Testing Seller Pages Styling")
    print("=" * 40)
    
    # Create test client
    client = Client()
    
    # Try to get demo seller
    try:
        user = User.objects.get(username='demoseller')
        print(f"✅ Demo seller found: {user.username}")
        
        # Login as demo seller
        login_success = client.login(username='demoseller', password='demo123')
        if login_success:
            print("✅ Successfully logged in as demo seller")
            
            # Test Add Product page
            response = client.get('/add-product/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'seller.css' in content:
                    print("✅ Add Product page loads with seller.css styling")
                else:
                    print("⚠️  Add Product page loads but no seller.css found")
                
                if 'seller-page' in content:
                    print("✅ Add Product page has seller-page CSS class")
                else:
                    print("⚠️  Add Product page missing seller-page CSS class")
            else:
                print(f"❌ Add Product page failed to load: {response.status_code}")
            
            # Test My Products page
            response = client.get('/my-products/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'seller.css' in content:
                    print("✅ My Products page loads with seller.css styling")
                else:
                    print("⚠️  My Products page loads but no seller.css found")
                
                if 'seller-page' in content:
                    print("✅ My Products page has seller-page CSS class")
                else:
                    print("⚠️  My Products page missing seller-page CSS class")
            else:
                print(f"❌ My Products page failed to load: {response.status_code}")
                
        else:
            print("❌ Failed to login as demo seller")
            
    except User.DoesNotExist:
        print("❌ Demo seller not found. Run create_demo_seller.py first.")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Seller pages styling test completed!")
    return True

if __name__ == "__main__":
    test_seller_pages()