import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os
import numpy as np

# Enhanced dataset with more realistic financial data
np.random.seed(42)

# Generate more comprehensive training data
n_samples = 1000
incomes = np.random.normal(45000, 20000, n_samples)  # Mean income 45k, std 20k
incomes = np.clip(incomes, 15000, 150000)  # Clip to realistic range

ages = np.random.normal(35, 12, n_samples)  # Mean age 35, std 12
ages = np.clip(ages, 18, 70)  # Clip to realistic range

# Create credit scores based on income and age with some noise
base_scores = (incomes / 1000) * 8 + (ages - 18) * 2 + np.random.normal(0, 50, n_samples)
credit_scores = np.clip(base_scores, 300, 850)  # Standard credit score range

# Create DataFrame
data = pd.DataFrame({
    'income': incomes.astype(int),
    'age': ages.astype(int),
    'credit_score': credit_scores.astype(int)
})

# Features and target
X = data[['income', 'age']]
y = data['credit_score']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model with better parameters
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    min_samples_split=5,
    min_samples_leaf=2
)

model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print(f"Model Performance:")
print(f"Mean Absolute Error: {mae:.2f}")
print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# Create model folder if not exists
if not os.path.exists("model"):
    os.mkdir("model")

# Save model
joblib.dump(model, "model/credit_model.pkl")
print("✅ Enhanced AI Credit Scoring Model trained & saved successfully!")

# Display feature importance
feature_importance = model.feature_importances_
features = ['Income', 'Age']
print("\nFeature Importance:")
for feature, importance in zip(features, feature_importance):
    print(f"{feature}: {importance:.3f}")
