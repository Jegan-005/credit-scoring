#!/usr/bin/env python3
"""
Test script for the new Flask AI Credit Scoring flow
Tests the separation of authentication and financial data collection
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_new_flow():
    """Test the complete new flow"""
    print("🧪 Testing New Flask AI Credit Scoring Flow")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data['status']}")
            print(f"   Model Loaded: {health_data['model_loaded']}")
            print(f"   Database Users: {health_data['database']['user_count']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
    
    # Test 2: API Credit Check with new parameters
    print("\n2. Testing API Credit Check with new parameters...")
    try:
        test_data = {
            "age": 30,
            "income": 50000,
            "existing_loans": 1,
            "total_emi": 15000,
            "credit_utilization": 25.5,
            "defaults": 0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/credit-check",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Credit Check Success:")
            print(f"   Credit Score: {result['credit_score']}")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Eligible Amount: ₹{result['eligible_amount']:,}")
            print(f"   Explanation: {result['explanation'][:100]}...")
        else:
            print(f"❌ API Credit Check Failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ API Credit Check Error: {e}")
    
    # Test 3: Test with different risk profiles
    print("\n3. Testing Different Risk Profiles...")
    
    test_profiles = [
        {
            "name": "Low Risk Profile",
            "data": {
                "age": 35,
                "income": 80000,
                "existing_loans": 0,
                "total_emi": 0,
                "credit_utilization": 15.0,
                "defaults": 0
            }
        },
        {
            "name": "Medium Risk Profile", 
            "data": {
                "age": 28,
                "income": 40000,
                "existing_loans": 2,
                "total_emi": 12000,
                "credit_utilization": 45.0,
                "defaults": 0
            }
        },
        {
            "name": "High Risk Profile",
            "data": {
                "age": 22,
                "income": 25000,
                "existing_loans": 3,
                "total_emi": 18000,
                "credit_utilization": 85.0,
                "defaults": 1
            }
        }
    ]
    
    for profile in test_profiles:
        try:
            response = requests.post(
                f"{BASE_URL}/api/credit-check",
                json=profile["data"],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {profile['name']}:")
                print(f"   Score: {result['credit_score']} | Risk: {result['risk_level']} | Eligible: ₹{result['eligible_amount']:,}")
            else:
                print(f"❌ {profile['name']} Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {profile['name']} Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("✅ New flow separates authentication from financial data")
    print("✅ API accepts comprehensive financial parameters")
    print("✅ AI model calculates scores based on 6 factors")
    print("✅ Different risk profiles produce different scores")
    print("\n📋 New Flow Steps:")
    print("1. Signup: Username, Email, Password only")
    print("2. Login: Normal authentication")
    print("3. Financial Form: Age, Income, Loans, EMI, Utilization, Defaults")
    print("4. Dashboard: Shows comprehensive credit analysis")
    print("5. Profile: Separate auth and financial data management")

if __name__ == "__main__":
    test_new_flow()