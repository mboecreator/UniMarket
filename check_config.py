#!/usr/bin/env python3
"""
Configuration Check Script for UniMarket
This script verifies that all configurations are working properly.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_market_backend.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from accounts.models import UserProfile
from products.models import Category, Product

def check_database_connection():
    """Check if database connection is working"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Database connection: OK")
                return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False

def check_models():
    """Check if all models are working"""
    try:
        # Check User model
        user_count = User.objects.count()
        print(f"✅ User model: OK ({user_count} users)")
        
        # Check UserProfile model
        profile_count = UserProfile.objects.count()
        print(f"✅ UserProfile model: OK ({profile_count} profiles)")
        
        # Check Category model
        category_count = Category.objects.count()
        print(f"✅ Category model: OK ({category_count} categories)")
        
        # Check Product model
        product_count = Product.objects.count()
        print(f"✅ Product model: OK ({product_count} products)")
        
        return True
    except Exception as e:
        print(f"❌ Models check: FAILED - {e}")
        return False

def check_static_files():
    """Check if static files are configured properly"""
    try:
        static_url = settings.STATIC_URL
        static_root = getattr(settings, 'STATIC_ROOT', None)
        staticfiles_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        
        print(f"✅ Static files configuration:")
        print(f"   - STATIC_URL: {static_url}")
        print(f"   - STATIC_ROOT: {static_root}")
        print(f"   - STATICFILES_DIRS: {staticfiles_dirs}")
        
        # Check if CSS file exists
        css_path = '/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket/frontend/static/css/style.css'
        if os.path.exists(css_path):
            print("   - CSS file: EXISTS")
        else:
            print("   - CSS file: MISSING")
            
        # Check if JS file exists
        js_path = '/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket/frontend/static/js/auth.js'
        if os.path.exists(js_path):
            print("   - Auth JS file: EXISTS")
        else:
            print("   - Auth JS file: MISSING")
        
        return True
    except Exception as e:
        print(f"❌ Static files check: FAILED - {e}")
        return False

def check_templates():
    """Check if templates exist"""
    try:
        template_dir = '/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket/frontend/templates'
        
        required_templates = [
            'base.html',
            'accounts/login.html',
            'accounts/register.html',
            'products/add_product.html',
            'products/home.html'
        ]
        
        print("✅ Template files:")
        all_exist = True
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                print(f"   - {template}: EXISTS")
            else:
                print(f"   - {template}: MISSING")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"❌ Templates check: FAILED - {e}")
        return False

def check_authentication_urls():
    """Check if authentication URLs are configured"""
    try:
        from django.urls import reverse
        
        urls_to_check = [
            ('login', 'Login URL'),
            ('register', 'Register URL'),
            ('logout', 'Logout URL'),
            ('profile', 'Profile URL'),
        ]
        
        print("✅ Authentication URLs:")
        for url_name, description in urls_to_check:
            try:
                url = reverse(url_name)
                print(f"   - {description}: {url}")
            except Exception as e:
                print(f"   - {description}: FAILED - {e}")
        
        return True
    except Exception as e:
        print(f"❌ URL check: FAILED - {e}")
        return False

def main():
    """Run all configuration checks"""
    print("🔍 UniMarket Configuration Check")
    print("=" * 40)
    
    checks = [
        check_database_connection,
        check_models,
        check_static_files,
        check_templates,
        check_authentication_urls,
    ]
    
    results = []
    for check in checks:
        print()
        result = check()
        results.append(result)
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All checks passed! Your UniMarket configuration is ready.")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
    
    print("\n📊 Summary:")
    print(f"Database: {'PostgreSQL' if 'postgresql' in settings.DATABASES['default']['ENGINE'] else 'SQLite'}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Secret Key: {'Set' if settings.SECRET_KEY else 'Missing'}")

if __name__ == "__main__":
    main()