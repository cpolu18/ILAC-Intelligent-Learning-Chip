
import pandas as pd

# Load the ILAC feature dataset
df = pd.read_csv("ilac_features.csv")

print("\nILAC MACHINE LEARNING READINESS")
print("=" * 45)

# Dataset size
print("\n1. Dataset Size")
print("Total records:", len(df))
print("Total features:", len(df.columns))

# Performance label distribution
print("\n2. Performance Label Distribution")
print(df["performance_level"].value_counts())

# Student count
print("\n3. Number of Students")
print(df["student_name"].nunique())

# Subject coverage
print("\n4. Subject Coverage")
print(df["subject"].value_counts())

# Concept coverage
print("\n5. Concept Coverage")
print(df["concept"].value_counts())

# ML readiness
print("\n6. Readiness Assessment")

if len(df) < 30:
    print("WARNING: Very small dataset.")
    print("More student records are needed for meaningful ML training.")
else:
    print("Dataset has at least 30 records.")
    print("Further checks are needed before training.")

print("\nINSPECTION COMPLETED")
print("=" * 45)
