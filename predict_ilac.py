
import pandas as pd
import joblib

# Load trained ILAC model
model = joblib.load("ilac_model.pkl")

print("\nILAC STUDENT PERFORMANCE PREDICTION")
print("=" * 45)

# Enter new student performance data
total_questions = 10
correct_answers = 3
incorrect_answers = 7
quiz_attempts = 2

# Prepare input in the same format used during training
student_data = pd.DataFrame([{
    "total_questions": total_questions,
    "correct_answers": correct_answers,
    "incorrect_answers": incorrect_answers,
    "quiz_attempts": quiz_attempts
}])

# Predict performance
prediction = model.predict(student_data)

# Calculate accuracy for display
accuracy = (
    correct_answers / total_questions
) * 100

print("\nStudent Performance Details")
print("Total Questions:", total_questions)
print("Correct Answers:", correct_answers)
print("Incorrect Answers:", incorrect_answers)
print("Accuracy:", round(accuracy, 2), "%")
print("Quiz Attempts:", quiz_attempts)

print("\nILAC MODEL PREDICTION")
print("Predicted Performance:", prediction[0])

print("\nPREDICTION COMPLETED")
print("=" * 45)
