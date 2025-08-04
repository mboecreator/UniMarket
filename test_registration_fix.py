#!/usr/bin/env python3
"""
Test Registration Fix
This script tests that the registration issue is fixed.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/user/Documents/PERSONAL DOC/MY BEST FOLDER/44git22 /my projects/UniMarket')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_market_backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def test_registration_fix():
    """Test that we can create multiple users without student_id conflicts"""
    print("🧪 Testing Registration Fix")
    print("=" * 40)
    
    # Clean up any existing test users
    test_usernames = ['testuser1', 'testuser2', 'testuser3']
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"🧹 Cleaned up existing user: {username}")
        except User.DoesNotExist:
            pass
    
    # Test creating multiple users
    success_count = 0
    
    for i, username in enumerate(test_usernames, 1):
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=f'{username}@university.edu',
                password='testpass123'
            )
            
            # Create profile (this was causing the error before)
            profile = UserProfile.objects.create(
                user=user,
                student_id=None,  # This should not cause conflicts now
                university='',
            )
            
            print(f"✅ User {i}: {username} created successfully")
            success_count += 1
            
        except Exception as e:
            print(f"❌ User {i}: {username} failed - {e}")
    
    print(f"\n📊 Results: {success_count}/{len(test_usernames)} users created successfully")
    
    if success_count == len(test_usernames):
        print("🎉 Registration fix is working correctly!")
        return True
    else:
        print("❌ Registration fix needs more work")
        return False

def cleanup():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    test_usernames = ['testuser1', 'testuser2', 'testuser3']
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"✅ Deleted: {username}")
        except User.DoesNotExist:
            pass

def main():
    """Run the test"""
    try:
        success = test_registration_fix()
        
        if success:
            print("\n" + "=" * 40)
            print("✅ REGISTRATION FIX VERIFIED!")
            print("Users can now register without student_id conflicts.")
        else:
            print("\n" + "=" * 40)
            print("❌ Registration fix needs attention.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    finally:
        cleanup()
        print("\n✨ Test completed.")

if __name__ == "__main__":
    main()