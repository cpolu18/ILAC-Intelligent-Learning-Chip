
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load processed student data
FILE = Path("ilac_features.csv")

if not FILE.exists():
    print("Error: ilac_features.csv not found.")
    raise SystemExit

df = pd.read_csv(FILE)

if df.empty:
    print("No student performance data available.")
    raise SystemExit

# --------------------------------
# GRAPH 1: Concept-wise accuracy
# --------------------------------

concept_accuracy = (
    df.groupby("concept")["accuracy"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(9, 5))

concept_accuracy.plot(kind="bar")

plt.title("ILAC - Average Accuracy by Concept")
plt.xlabel("Concept")
plt.ylabel("Average Accuracy (%)")
plt.ylim(0, 100)
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

plt.savefig("concept_accuracy.png")
plt.close()

# --------------------------------
# GRAPH 2: Performance distribution
# --------------------------------

performance_count = (
    df["performance_level"]
    .value_counts()
    .reindex(["Weak", "Average", "Good"], fill_value=0)
)

plt.figure(figsize=(7, 5))

performance_count.plot(kind="bar")

plt.title("ILAC - Student Performance Distribution")
plt.xlabel("Performance Level")
plt.ylabel("Number of Concept Records")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig("performance_distribution.png")
plt.close()

# --------------------------------
# Display summary
# --------------------------------

print("\nILAC DATA VISUALIZATION")
print("-----------------------")

print("\nAverage accuracy by concept:")
print(concept_accuracy)

print("\nPerformance distribution:")
print(performance_count)

print("\nGraphs generated successfully:")
print("1. concept_accuracy.png")
print("2. performance_distribution.png")
