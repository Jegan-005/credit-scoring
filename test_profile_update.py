#!/usr/bin/env python3
"""
Test Profile Update Functionality
"""

from database import init_db, create_user, get_user_by_username, update_user_profile

def test_profile_update():
    print("🧪 Testing Profile Update Functionality")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Create test user
    test_username = "test_profile_user"
    success, message, user_id = create_user(
        username=test_username,
        password="testpass123",
        email="test@example.com",
        age=25,
        income=30000
    )
    
    if success:
        print(f"✅ Test user created: {test_username}")
    else:
        print(f"ℹ️ User might already exist: {message}")
    
    # Get original data
    original_data = get_user_by_username(test_username)
    print(f"\n📊 Original Data:")
    print(f"   Email: {original_data['email']}")
    print(f"   Age: {original_data['age']}")
    print(f"   Income: {original_data['income']}")
    
    # Test profile update
    print(f"\n🔄 Testing profile update...")
    success, message = update_user_profile(
        username=test_username,
        email="updated@example.com",
        age=28,
        income=45000
    )
    
    if success:
        print(f"✅ Profile update successful: {message}")
    else:
        print(f"❌ Profile update failed: {message}")
        return
    
    # Verify update
    updated_data = get_user_by_username(test_username)
    print(f"\n📊 Updated Data:")
    print(f"   Email: {updated_data['email']}")
    print(f"   Age: {updated_data['age']}")
    print(f"   Income: {updated_data['income']}")
    
    # Check if data actually changed
    if (updated_data['email'] == "updated@example.com" and 
        updated_data['age'] == 28 and 
        updated_data['income'] == 45000):
        print(f"\n✅ Profile update verification PASSED!")
        print(f"   All fields updated correctly in database")
    else:
        print(f"\n❌ Profile update verification FAILED!")
        print(f"   Data not properly saved to database")

if __name__ == "__main__":
    test_profile_update()