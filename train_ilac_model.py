
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# 1. Load demonstration dataset
df = pd.read_csv("ilac_demo_training.csv")

print("\nILAC DECISION TREE MODEL")
print("=" * 45)

# 2. Select input features
X = df[
    [
        "total_questions",
        "correct_answers",
        "incorrect_answers",
        "quiz_attempts"
    ]
]

# 3. Select target output
y = df["performance_level"]

# 4. Split dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# 5. Create Decision Tree model
model = DecisionTreeClassifier(
    max_depth=4,
    random_state=42
)

# 6. Train the model
model.fit(X_train, y_train)

print("\nMODEL TRAINING COMPLETED")

# 7. Predict test data
y_pred = model.predict(X_test)

# 8. Evaluate model
accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred, labels=["Weak", "Average", "Good"]))

# 9. Save trained model
joblib.dump(model, "ilac_model.pkl")

print("\nModel saved as ilac_model.pkl")

print("\nTRAINING PROCESS COMPLETED")
print("=" * 45)
