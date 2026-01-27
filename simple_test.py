#!/usr/bin/env python3
"""
Simple test for profile update functionality
"""

from database import get_user_by_username, update_user_profile

# Test the profile update
test_username = "test_profile_user"

print("🧪 Simple Profile Update Test")
print("=" * 40)

# Get current data
user_data = get_user_by_username(test_username)
if user_data:
    print(f"✅ Found user: {test_username}")
    print(f"   Current income: ₹{user_data['income']:,}")
    
    # Update income
    new_income = 50000
    success, message = update_user_profile(test_username, income=new_income)
    
    if success:
        print(f"✅ Update successful: {message}")
        
        # Verify update
        updated_data = get_user_by_username(test_username)
        print(f"   New income: ₹{updated_data['income']:,}")
        
        if updated_data['income'] == new_income:
            print("✅ Profile update verification PASSED!")
        else:
            print("❌ Profile update verification FAILED!")
    else:
        print(f"❌ Update failed: {message}")
else:
    print(f"❌ User {test_username} not found")