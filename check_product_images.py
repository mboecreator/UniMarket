#!/usr/bin/env python3
"""
Check Product Images
Diagnostic script to check if products have images and if they're accessible.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_market_backend.settings')
django.setup()

from products.models import Product
from django.conf import settings

def check_product_images():
    """Check all products and their images"""
    print("🔍 Checking Product Images")
    print("=" * 50)
    
    products = Product.objects.all()
    print(f"📊 Total products in database: {products.count()}")
    
    if products.count() == 0:
        print("❌ No products found in database!")
        return
    
    print("\n📋 Product Details:")
    print("-" * 50)
    
    for product in products:
        print(f"🏷️  Product: {product.title}")
        print(f"👤 Seller: {product.seller.username}")
        print(f"📅 Created: {product.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if product.image:
            print(f"🖼️  Image: {product.image.name}")
            print(f"📁 Image path: {product.image.path}")
            print(f"🌐 Image URL: {product.image.url}")
            
            # Check if file exists
            if os.path.exists(product.image.path):
                file_size = os.path.getsize(product.image.path)
                print(f"✅ File exists ({file_size} bytes)")
            else:
                print(f"❌ File does not exist at: {product.image.path}")
        else:
            print("❌ No image attached")
        
        print("-" * 30)
    
    # Check media directory
    print(f"\n📁 Media directory: {settings.MEDIA_ROOT}")
    products_media_dir = os.path.join(settings.MEDIA_ROOT, 'products')
    
    if os.path.exists(products_media_dir):
        files = os.listdir(products_media_dir)
        print(f"📂 Files in products media directory: {len(files)}")
        for file in files:
            file_path = os.path.join(products_media_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   📄 {file} ({file_size} bytes)")
    else:
        print("❌ Products media directory does not exist")
    
    print("\n" + "=" * 50)
    print("✅ Image check completed!")

if __name__ == "__main__":
    check_product_images()