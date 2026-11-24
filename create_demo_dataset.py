
import pandas as pd
import random

# Reproducible demonstration data
random.seed(42)

data = []

for i in range(120):

    total_questions = random.randint(1, 20)

    correct_answers = random.randint(
        0, total_questions
    )

    incorrect_answers = (
        total_questions - correct_answers
    )

    accuracy = (
        correct_answers / total_questions
    ) * 100

    quiz_attempts = random.randint(1, 5)

    # Generate performance labels
    if accuracy < 40:
        performance_level = "Weak"

    elif accuracy < 70:
        performance_level = "Average"

    else:
        performance_level = "Good"

    data.append({
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "accuracy": round(accuracy, 2),
        "quiz_attempts": quiz_attempts,
        "performance_level": performance_level
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save separate demonstration dataset
df.to_csv(
    "ilac_demo_training.csv",
    index=False
)

print("ILAC DEMO DATASET CREATED")
print("=" * 40)

print("Total records:", len(df))

print("\nPerformance Distribution:")
print(df["performance_level"].value_counts())

print("\nDataset Preview:")
print(df.head(10))

print("\nSaved as ilac_demo_training.csv")
