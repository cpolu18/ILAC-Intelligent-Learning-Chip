
import pandas as pd
from pathlib import Path

FILE = Path("ilac_features.csv")

print("\nILAC DATASET VALIDATION")
print("=" * 40)

# Check file availability
if not FILE.exists():
    print("ERROR: Dataset file not found.")
    raise SystemExit

# Load dataset
df = pd.read_csv(FILE)

# Check 1: Dataset size
print("\n1. Dataset Information")
print("Total records:", len(df))
print("Total columns:", len(df.columns))

if df.empty:
    print("ERROR: Dataset is empty.")
    raise SystemExit

# Check 2: Missing values
print("\n2. Missing Values")
missing = df.isnull().sum()
print(missing)

if missing.sum() == 0:
    print("No missing values found.")
else:
    print("WARNING: Missing values detected.")

# Check 3: Duplicate records
print("\n3. Duplicate Records")
duplicates = df.duplicated().sum()
print("Duplicate rows:", duplicates)

# Check 4: Accuracy range
print("\n4. Accuracy Validation")

invalid_accuracy = (
    (df["accuracy"] < 0) |
    (df["accuracy"] > 100)
).sum()

print("Invalid accuracy records:", invalid_accuracy)

# Check 5: Answer count validation
print("\n5. Answer Count Validation")

invalid_counts = (
    (df["correct_answers"] < 0) |
    (df["total_questions"] <= 0) |
    (df["correct_answers"] > df["total_questions"]) |
    (df["incorrect_answers"] < 0) |
    (df["correct_answers"] + df["incorrect_answers"]
     != df["total_questions"])
).sum()

print("Invalid answer count records:", invalid_counts)

# Check 6: Concept coverage
print("\n6. Subject and Concept Coverage")

print("\nSubjects:")
print(df["subject"].value_counts())

print("\nConcepts:")
print(df["concept"].value_counts())

# Final validation summary
print("\n" + "=" * 40)
print("VALIDATION SUMMARY")

checks_passed = (
    missing.sum() == 0
    and duplicates == 0
    and invalid_accuracy == 0
    and invalid_counts == 0
)

if checks_passed:
    print("Dataset passed the basic validation checks.")
else:
    print("Dataset needs cleaning or investigation.")

print("=" * 40)
