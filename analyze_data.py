
import pandas as pd
from pathlib import Path

# Input and output files
INPUT_FILE = Path("ilac_results.csv")
OUTPUT_FILE = Path("ilac_features.csv")

# Check whether the results file exists
if not INPUT_FILE.exists():
    print("Error: ilac_results.csv not found.")
    raise SystemExit

# Load student results
df = pd.read_csv(INPUT_FILE)

# Convert correctness column into Boolean values
df["is_correct"] = (
    df["is_correct"]
    .astype(str)
    .str.lower()
    .map({"true": True, "false": False})
)

# Check for invalid data
if df["is_correct"].isna().any():
    print("Error: Invalid values found in is_correct.")
    raise SystemExit

# Group data by student, subject and concept
features = (
    df.groupby(
        ["student_name", "subject", "concept"],
        as_index=False
    )
    .agg(
        total_questions=("question", "count"),
        correct_answers=("is_correct", "sum"),
        quiz_attempts=("timestamp", "nunique")
    )
)

# Calculate incorrect answers
features["incorrect_answers"] = (
    features["total_questions"]
    - features["correct_answers"]
)

# Calculate accuracy
features["accuracy"] = (
    features["correct_answers"]
    / features["total_questions"]
) * 100

# Classify performance using simple rules
def classify_performance(accuracy):
    if accuracy < 40:
        return "Weak"
    elif accuracy < 70:
        return "Average"
    else:
        return "Good"

features["performance_level"] = (
    features["accuracy"].apply(classify_performance)
)

# Save processed dataset
features.to_csv(OUTPUT_FILE, index=False)

# Display results
print("\nILAC STUDENT PERFORMANCE ANALYSIS")
print("----------------------------------")
print(features.to_string(index=False))

print("\nProcessed dataset saved as:", OUTPUT_FILE)
