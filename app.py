
import streamlit as st
import pandas as pd
import joblib

from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ILAC - Intelligent Learning Assistant Chip",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 ILAC")
st.subheader("Intelligent Learning Assistant Chip")
st.write(
    "Test your knowledge and discover which concepts "
    "need more practice."
)

# File paths
QUESTION_FILE = Path("ilac_questions.csv")
RESULT_FILE = Path("ilac_results.csv")
MODEL_FILE = Path("ilac_model.pkl")

# Load trained ML model
model = None

if MODEL_FILE.exists():
    try:
        model = joblib.load(MODEL_FILE)
    except Exception as error:
        st.warning(f"Could not load ML model: {error}")
else:
    st.warning("ILAC ML model file is missing.")

# Load questions
if not QUESTION_FILE.exists():
    st.error("ilac_questions.csv is missing.")
    st.stop()

try:
    df = pd.read_csv(QUESTION_FILE)
except Exception as error:
    st.error(f"Could not read question file: {error}")
    st.stop()

# Check required columns
required_columns = [
    "subject", "concept", "question",
    "option_a", "option_b", "option_c",
    "option_d", "correct_answer"
]

if not all(column in df.columns for column in required_columns):
    st.error("Your CSV file is missing required columns.")
    st.stop()

# Student details
st.header("Student Details")

student_name = st.text_input("Enter your name")

subjects = sorted(df["subject"].dropna().unique())

if len(subjects) == 0:
    st.error("No subjects found in the question bank.")
    st.stop()

selected_subject = st.selectbox("Select your subject", subjects)

# Filter questions
subject_questions = df[
    df["subject"] == selected_subject
].reset_index(drop=True)

st.divider()

st.header(f"{selected_subject} Quiz")
st.write(f"Total Questions: {len(subject_questions)}")

# Quiz form
with st.form("ilac_quiz_form"):

    for index, row in subject_questions.iterrows():

        st.markdown(f"### Question {index + 1}")
        st.write(f"**Concept:** {row['concept']}")
        st.write(row["question"])

        options = {
            "A": str(row["option_a"]),
            "B": str(row["option_b"]),
            "C": str(row["option_c"]),
            "D": str(row["option_d"])
        }

        st.radio(
            "Select your answer:",
            options=list(options.keys()),
            format_func=lambda letter, opts=options:
                f"{letter}. {opts[letter]}",
            key=f"answer_{selected_subject}_{index}"
        )

        st.divider()

    submitted = st.form_submit_button(
        "Submit Quiz",
        use_container_width=True
    )

# Process submitted answers
if submitted:

    if not student_name.strip():
        st.warning("Please enter your name before submitting.")

    else:
        records = []
        correct_count = 0

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        for index, row in subject_questions.iterrows():

            selected_answer = st.session_state.get(
                f"answer_{selected_subject}_{index}"
            )

            correct_answer = str(
                row["correct_answer"]
            ).strip().upper()

            is_correct = selected_answer == correct_answer

            if is_correct:
                correct_count += 1

            records.append({
                "timestamp": timestamp,
                "student_name": student_name.strip(),
                "subject": selected_subject,
                "concept": row["concept"],
                "question": row["question"],
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

        # Calculate score
        total_questions = len(subject_questions)

        accuracy = (
            correct_count / total_questions
        ) * 100

        incorrect_count = total_questions - correct_count

        # ML prediction
        ml_prediction = None

        if model is not None:

            student_features = pd.DataFrame([{
                "total_questions": total_questions,
                "correct_answers": correct_count,
                "incorrect_answers": incorrect_count,
                "quiz_attempts": 1
            }])

            try:
                ml_prediction = model.predict(
                    student_features
                )[0]

            except Exception as error:
                st.warning(f"ML prediction failed: {error}")

        # Save results
        new_results = pd.DataFrame(records)

        if RESULT_FILE.exists():

            old_results = pd.read_csv(RESULT_FILE)

            all_results = pd.concat(
                [old_results, new_results],
                ignore_index=True
            )

        else:
            all_results = new_results

        all_results.to_csv(
            RESULT_FILE,
            index=False
        )

        # Store result for display
        st.session_state["last_result"] = {
            "student": student_name.strip(),
            "subject": selected_subject,
            "correct": correct_count,
            "total": total_questions,
            "accuracy": accuracy,
            "records": records,
            "ml_prediction": ml_prediction
        }

# Display results
result = st.session_state.get("last_result")

if result and result["subject"] == selected_subject:

    st.divider()
    st.header("📊 Your Quiz Results")

    col1, col2, col3 = st.columns(3)

    col1.metric("Correct Answers", result["correct"])
    col2.metric("Total Questions", result["total"])
    col3.metric("Accuracy", f"{result['accuracy']:.1f}%")

    st.progress(result["accuracy"] / 100)

    # Machine learning prediction
    st.subheader("🤖 ILAC Machine Learning Prediction")

    if result["ml_prediction"] is not None:

        st.success(
            f"Predicted Performance: "
            f"{result['ml_prediction']}"
        )

        st.caption(
            "This prediction uses the current demonstration "
            "model trained on synthetic data. It is not yet "
            "validated for real student performance."
        )

    else:
        st.warning("ML prediction is currently unavailable.")

    # Concept-wise performance
    result_df = pd.DataFrame(result["records"])

    concept_performance = (
        result_df.groupby("concept")["is_correct"]
        .mean() * 100
    )

    st.subheader("Concept-wise Performance")

    for concept, score in concept_performance.items():

        st.write(f"**{concept}: {score:.1f}%**")
        st.progress(score / 100)

        if score < 40:
            st.warning(f"Practice {concept} more.")

        elif score < 70:
            st.info(f"Keep improving in {concept}.")

        else:
            st.success(f"Good performance in {concept}!")

    # Answer review
    st.subheader("Answer Review")

    for index, record in enumerate(result["records"]):

        st.write(
            f"**Question {index + 1}:** "
            f"{record['question']}"
        )

        if record["is_correct"]:

            st.success(
                f"Correct! Your answer: "
                f"{record['selected_answer']}"
            )

        else:

            st.error(
                f"Your answer: {record['selected_answer']} | "
                f"Correct answer: {record['correct_answer']}"
            )

st.divider()

st.caption(
    "ILAC Project | Learning through intelligent analysis"
)
