#!/usr/bin/env python3
"""
Test script for CredX AI Database functionality
"""

from database import (
    init_db, create_user, authenticate_user, get_user_by_username,
    update_user_profile, database_health_check, get_user_count
)

def test_database():
    print("🧪 Testing CredX AI Database...")
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    
    # Health check
    print("\n2. Database health check...")
    health = database_health_check()
    print(f"   Status: {health['status']}")
    print(f"   Users: {health.get('user_count', 0)}")
    print(f"   Size: {health.get('database_size_kb', 0)} KB")
    
    # Test user creation
    print("\n3. Testing user creation...")
    success, message, user_id = create_user(
        username="testuser",
        password="testpass123",
        email="test@credx.com",
        age=28,
        income=45000
    )
    print(f"   Create user: {success} - {message}")
    if success:
        print(f"   User ID: {user_id}")
    
    # Test duplicate user creation
    print("\n4. Testing duplicate user creation...")
    success, message, _ = create_user(
        username="testuser",
        password="different",
        email="different@credx.com",
        age=30,
        income=50000
    )
    print(f"   Duplicate user: {success} - {message}")
    
    # Test authentication
    print("\n5. Testing authentication...")
    success, user_data, message = authenticate_user("testuser", "testpass123")
    print(f"   Auth success: {success} - {message}")
    if success:
        print(f"   User data: {user_data['username']}, Age: {user_data['age']}, Income: {user_data['income']}")
    
    # Test wrong password
    print("\n6. Testing wrong password...")
    success, user_data, message = authenticate_user("testuser", "wrongpass")
    print(f"   Wrong password: {success} - {message}")
    
    # Test get user by username
    print("\n7. Testing get user by username...")
    user_data = get_user_by_username("testuser")
    if user_data:
        print(f"   Found user: {user_data['username']}, Email: {user_data['email']}")
    else:
        print("   User not found")
    
    # Test profile update
    print("\n8. Testing profile update...")
    success, message = update_user_profile("testuser", age=29, income=48000)
    print(f"   Update profile: {success} - {message}")
    
    # Verify update
    user_data = get_user_by_username("testuser")
    if user_data:
        print(f"   Updated data: Age: {user_data['age']}, Income: {user_data['income']}")
    
    # Final stats
    print("\n9. Final statistics...")
    total_users = get_user_count()
    print(f"   Total users in database: {total_users}")
    
    print("\n✅ Database test completed!")

if __name__ == "__main__":
    test_database()