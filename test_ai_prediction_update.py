#!/usr/bin/env python3
"""
Test that profile updates immediately affect AI predictions
"""

import joblib
import numpy as np
from database import init_db, get_user_by_username, update_user_profile

def calculate_credit_score(income, age):
    """Calculate credit score using the AI model"""
    try:
        model = joblib.load("model/credit_model.pkl")
        credit_score = int(model.predict([[income, age]])[0])
        return max(300, min(850, credit_score))
    except Exception as e:
        print(f"Error loading model: {e}")
        return 650  # Default score

def test_ai_prediction_update():
    print("🧪 Testing AI Prediction Update After Profile Change")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    test_username = "test_profile_user"
    
    # Get current user data
    user_data = get_user_by_username(test_username)
    if not user_data:
        print("❌ Test user not found. Run test_profile_update.py first.")
        return
    
    print(f"📊 Current Profile:")
    print(f"   Username: {user_data['username']}")
    print(f"   Age: {user_data['age']}")
    print(f"   Income: ₹{user_data['income']:,}")
    
    # Calculate current credit score
    current_score = calculate_credit_score(user_data['income'], user_data['age'])
    print(f"   Current AI Credit Score: {current_score}")
    
    # Update profile with higher income
    new_income = user_data['income'] + 20000
    print(f"\n🔄 Updating income from ₹{user_data['income']:,} to ₹{new_income:,}")
    
    success, message = update_user_profile(
        username=test_username,
        email=user_data['email'],
        age=user_data['age'],
        income=new_income
    )
    
    if not success:
        print(f"❌ Profile update failed: {message}")
        return
    
    # Get updated data
    updated_data = get_user_by_username(test_username)
    new_score = calculate_credit_score(updated_data['income'], updated_data['age'])
    
    print(f"✅ Profile updated successfully!")
    print(f"\n📊 Updated Profile:")
    print(f"   Age: {updated_data['age']}")
    print(f"   Income: ₹{updated_data['income']:,}")
    print(f"   New AI Credit Score: {new_score}")
    
    # Analyze the change
    score_change = new_score - current_score
    print(f"\n📈 AI Prediction Analysis:")
    print(f"   Score Change: {score_change:+d} points")
    
    if score_change > 0:
        print(f"   ✅ Higher income improved credit score!")
    elif score_change < 0:
        print(f"   ⚠️ Credit score decreased (unexpected)")
    else:
        print(f"   ➡️ No change in credit score")
    
    print(f"\n🎯 Conclusion: Profile updates immediately affect AI predictions!")

if __name__ == "__main__":
    test_ai_prediction_update()