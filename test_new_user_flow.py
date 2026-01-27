#!/usr/bin/env python3

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_new_user_flow():
    """Test the complete new user flow: Signup → Login → Financial Form → Dashboard"""
    
    print("🧪 Testing New User Flow...")
    print("=" * 50)
    
    # Create a unique test user
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_username = f"testuser_{timestamp}"
    test_email = f"test_{timestamp}@example.com"
    test_password = "testpass123"
    
    session = requests.Session()
    
    # Step 1: Test Signup
    print(f"1️⃣ Testing Signup for user: {test_username}")
    signup_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password
    }
    
    signup_response = session.post(f"{BASE_URL}/signup", data=signup_data)
    if signup_response.status_code == 200 and "login" in signup_response.url:
        print("✅ Signup successful - redirected to login")
    else:
        print(f"❌ Signup failed - Status: {signup_response.status_code}")
        return False
    
    # Step 2: Test Login
    print("2️⃣ Testing Login")
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    if login_response.status_code == 200 and "financial-form" in login_response.url:
        print("✅ Login successful - redirected to financial form")
    else:
        print(f"❌ Login failed - Status: {login_response.status_code}")
        return False
    
    # Step 3: Test Financial Form Submission
    print("3️⃣ Testing Financial Form Submission")
    financial_data = {
        "age": "28",
        "income": "45000",
        "existing_loans": "1",
        "total_emi": "8000",
        "credit_utilization": "35.5",
        "defaults": "no"
    }
    
    financial_response = session.post(f"{BASE_URL}/financial-form", data=financial_data)
    if financial_response.status_code == 200 and "dashboard" in financial_response.url:
        print("✅ Financial form submission successful - redirected to dashboard")
    else:
        print(f"❌ Financial form submission failed - Status: {financial_response.status_code}")
        print("Response content:", financial_response.text[:500])
        return False
    
    # Step 4: Test Dashboard Access
    print("4️⃣ Testing Dashboard Access")
    dashboard_response = session.get(f"{BASE_URL}/dashboard")
    if dashboard_response.status_code == 200 and "Credit Score" in dashboard_response.text:
        print("✅ Dashboard access successful - credit score displayed")
    else:
        print(f"❌ Dashboard access failed - Status: {dashboard_response.status_code}")
        return False
    
    print("=" * 50)
    print("🎉 ALL TESTS PASSED! New user flow works perfectly!")
    print(f"✅ User {test_username} can: Signup → Login → Fill Financial Form → View Dashboard")
    return True

def test_database_operations():
    """Test database operations directly"""
    print("\n🗄️ Testing Database Operations...")
    print("=" * 50)
    
    from database import (
        create_user, authenticate_user, save_user_financials, 
        get_user_financials, has_financial_data
    )
    
    # Test user creation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_username = f"dbtest_{timestamp}"
    test_email = f"dbtest_{timestamp}@example.com"
    
    success, message, user_id = create_user(test_username, "testpass", test_email)
    if success:
        print(f"✅ User creation successful: {test_username} (ID: {user_id})")
    else:
        print(f"❌ User creation failed: {message}")
        return False
    
    # Test authentication
    auth_success, user_data, auth_message = authenticate_user(test_username, "testpass")
    if auth_success:
        print(f"✅ Authentication successful: {user_data['username']}")
    else:
        print(f"❌ Authentication failed: {auth_message}")
        return False
    
    # Test financial data operations
    print("📊 Testing financial data operations...")
    
    # Check if user has financial data (should be False for new user)
    has_data = has_financial_data(test_username)
    if not has_data:
        print("✅ New user correctly has no financial data")
    else:
        print("❌ New user incorrectly shows as having financial data")
        return False
    
    # Save financial data
    save_success, save_message = save_user_financials(
        test_username, 30, 50000, 2, 12000, 40.0, 0
    )
    if save_success:
        print("✅ Financial data saved successfully")
    else:
        print(f"❌ Financial data save failed: {save_message}")
        return False
    
    # Retrieve financial data
    financial_data = get_user_financials(test_username)
    if financial_data and financial_data['age'] == 30:
        print("✅ Financial data retrieved successfully")
    else:
        print("❌ Financial data retrieval failed")
        return False
    
    # Check if user now has financial data
    has_data_after = has_financial_data(test_username)
    if has_data_after:
        print("✅ User correctly shows as having financial data after save")
    else:
        print("❌ User incorrectly shows as not having financial data after save")
        return False
    
    print("=" * 50)
    print("🎉 ALL DATABASE TESTS PASSED!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Comprehensive New User Flow Tests")
    print("=" * 60)
    
    # Test database operations first
    db_success = test_database_operations()
    
    if db_success:
        # Test web flow
        web_success = test_new_user_flow()
        
        if web_success:
            print("\n🎊 COMPLETE SUCCESS!")
            print("✅ Database operations work correctly")
            print("✅ Web application flow works correctly")
            print("✅ New users can successfully: Signup → Login → Financial Form → Dashboard")
        else:
            print("\n⚠️ Database tests passed but web flow failed")
    else:
        print("\n❌ Database tests failed - skipping web flow tests")