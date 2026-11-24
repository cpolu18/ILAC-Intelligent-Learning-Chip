
import pandas as pd

# Load the processed ILAC dataset
df = pd.read_csv("ilac_features.csv")

print("\nILAC DATASET INSPECTION")
print("=" * 45)

# Dataset size
print("\n1. Dataset Size")
print("Total records:", len(df))
print("Total columns:", len(df.columns))

# Available columns
print("\n2. Available Features")
print(df.columns.tolist())

# Number of students
print("\n3. Student Information")
print("Unique students:", df["student_name"].nunique())

# Performance category distribution
print("\n4. Performance Category Distribution")
print(df["performance_level"].value_counts())

# Subject distribution
print("\n5. Subject Distribution")
print(df["subject"].value_counts())

# Display all records
print("\n6. Dataset Preview")
print(df.to_string(index=False))

print("\n" + "=" * 45)
print("INSPECTION COMPLETED")
