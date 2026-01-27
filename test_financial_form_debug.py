#!/usr/bin/env python3

import requests
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_financial_form_debug():
    """Test financial form submission with detailed debugging"""
    
    print("🧪 Testing Financial Form with Debug Logging...")
    print("=" * 50)
    
    # Create a unique test user
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_username = f"formtest_{timestamp}"
    test_email = f"formtest_{timestamp}@example.com"
    test_password = "testpass123"
    
    session = requests.Session()
    
    # Step 1: Signup
    print(f"1️⃣ Creating test user: {test_username}")
    signup_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password
    }
    
    signup_response = session.post(f"{BASE_URL}/signup", data=signup_data)
    if signup_response.status_code != 200 or "login" not in signup_response.url:
        print(f"❌ Signup failed - Status: {signup_response.status_code}")
        return False
    print("✅ Signup successful")
    
    # Step 2: Login
    print("2️⃣ Logging in...")
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    if login_response.status_code != 200 or "financial-form" not in login_response.url:
        print(f"❌ Login failed - Status: {login_response.status_code}")
        return False
    print("✅ Login successful")
    
    # Step 3: Submit Financial Form
    print("3️⃣ Submitting financial form...")
    financial_data = {
        "age": "28",
        "income": "45000",
        "existing_loans": "1",
        "total_emi": "8000",
        "credit_utilization": "35.5",
        "defaults": "0"
    }
    
    print(f"📋 Form data being sent: {financial_data}")
    
    financial_response = session.post(f"{BASE_URL}/financial-form", data=financial_data)
    
    print(f"📊 Response Status: {financial_response.status_code}")
    print(f"📊 Response URL: {financial_response.url}")
    
    if financial_response.status_code == 200:
        if "dashboard" in financial_response.url:
            print("✅ Financial form submission successful - redirected to dashboard")
            return True
        elif "financial-form" in financial_response.url:
            print("⚠️ Stayed on financial form - checking for error message")
            if "error" in financial_response.text.lower():
                print("❌ Error found in response")
                # Extract error message
                import re
                error_match = re.search(r'<div class="error-message">(.*?)</div>', financial_response.text)
                if error_match:
                    print(f"❌ Error message: {error_match.group(1)}")
                else:
                    print("❌ Error present but couldn't extract message")
            return False
        else:
            print(f"⚠️ Unexpected redirect to: {financial_response.url}")
            return False
    else:
        print(f"❌ HTTP Error: {financial_response.status_code}")
        return False

if __name__ == "__main__":
    test_financial_form_debug()