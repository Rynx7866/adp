import streamlit as st
from datetime import date
import sqlite3
import plotly.express as px
import matplotlib.pyplot as plt
# Page Configuration
st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 AI Study Planner")
st.markdown("Plan your studies intelligently and stay ahead of your exams.")

# Sidebar
st.sidebar.header("Student Information")

student_name = st.sidebar.text_input("Student Name")
daily_hours = st.sidebar.number_input(
    "Available Study Hours per Day",
    min_value=1,
    max_value=24,
    value=6
)

if student_name:
    st.markdown(f"## 👋 Welcome, {student_name}!")

# Main Form
st.header("➕ Add Subject")

col1, col2 = st.columns(2)

with col1:
    subject = st.text_input("Subject Name")
    
    difficulty = st.slider(
        "Difficulty Level",
        1,
        5,
        3
    )

with col2:
    remaining = st.slider(
        "Remaining Syllabus (%)",
        0,
        100,
        50
    )

    exam_date = st.date_input(
        "Exam Date",
        min_value=date.today()
    )

# Calculate days left
days_left = (exam_date - date.today()).days

# Preview Section
st.header("📋 Subject Preview")

col3, col4, col5 = st.columns(3)

with col3:
    st.metric("Difficulty", difficulty)

with col4:
    st.metric("Syllabus Left", f"{remaining}%")

with col5:
    st.metric("Days Until Exam", days_left)

# Priority Score
if days_left > 0:
    priority = (difficulty * remaining) / days_left
else:
    priority = 0

st.subheader("🎯 Priority Score")

st.progress(min(priority / 20, 1.0))

st.write(f"Priority Score: **{priority:.2f}**")

# Risk Analysis
st.subheader("⚠️ Risk Analysis")

if priority >= 20:
    st.error("High Risk - Immediate Attention Required")
elif priority >= 10:
    st.warning("Medium Risk - Needs Regular Study")
else:
    st.success("Low Risk - On Track")

# Save Button (Database will be added later)
if st.button("💾 Save Subject"):

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO subjects
    (subject_name, difficulty, remaining, exam_date, priority)
    VALUES (?, ?, ?, ?, ?)
    """, (
        subject,
        difficulty,
        remaining,
        str(exam_date),
        priority
    ))

    

    conn.commit()
    conn.close()

    st.success("Subject Saved Successfully!")

# Footer
st.markdown("---")
st.caption("AI Study Planner Project")

st.header("📚 Saved Subjects")

conn = sqlite3.connect("student.db")

import pandas as pd

df = pd.read_sql_query(
    "SELECT * FROM subjects",
    conn
)

conn.close()

st.dataframe(df)

st.markdown("---")
st.header("📅 Today's Study Timetable")

if not df.empty:

    total_priority = df["priority"].sum()

    df["Study Hours"] = (
        df["priority"] / total_priority
    ) * daily_hours

    df["Study Hours"] = df["Study Hours"].round(2)

    df = df.sort_values(
        by="priority",
        ascending=False
    )

    st.dataframe(
        df[
            [
                "subject_name",
                "priority",
                "Study Hours"
            ]
        ],
        use_container_width=True
    )

    top_subject = df.iloc[0]["subject_name"]

    st.error(
        f"🎯 Focus primarily on {top_subject} today!"
    )

    st.header("📊 Priority Analysis")

    fig, ax = plt.subplots(figsize=(6,3))

    bars = ax.bar(
         df["subject_name"],
         df["priority"],
         color=["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]
    )

    ax.set_title(
      "Subject Priority Comparison",
       fontsize=14,
       fontweight="bold"
    )

    ax.set_ylabel("Priority Score")

# Add values on top of bars
    for bar in bars:
        height = bar.get_height()

        ax.text(
           bar.get_x() + bar.get_width()/2,
           height,
           f"{height:.1f}",
           ha='center',
           va='bottom',
           fontsize=10
        )

    # Clean dashboard look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
         st.pyplot(fig)

    st.markdown("---")
    st.header("📝 Log Study Progress")

    subject_list = df["subject_name"].tolist()

    selected_subject = st.selectbox(
        "Select Subject",
        subject_list
    )

    completed_hours = st.number_input(
    "Hours Studied Today",
    min_value=0.0,
    max_value=24.0,
    step=0.5
    )

    if st.button("📌 Save Progress"):

       if completed_hours <= 0:
          st.error("Please enter hours greater than 0")

       else:

          conn = sqlite3.connect("student.db")
          cursor = conn.cursor()

          cursor.execute("""
          INSERT INTO progress
          (subject_name, study_date, completed_hours)
          VALUES (?, ?, ?)
          """, (
            selected_subject,
            str(date.today()),
            completed_hours
          ))

          conn.commit()
          conn.close()

          st.success("Progress Saved Successfully!")

conn = sqlite3.connect("student.db")
progress_df = pd.read_sql_query(
    "SELECT * FROM progress",
            conn
)

conn.close()

st.header("📚 Study Log")

st.dataframe(
    progress_df,
    use_container_width=True
)
total_completed = progress_df["completed_hours"].sum()

st.markdown("---")
st.header("📈 Productivity Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.metric(
       "Daily Goal",
        f"{daily_hours} Hours"
    )

with col2:
    st.metric(
        "Hours Completed",
        round(total_completed, 1)
    ) 

completion_rate = (
     total_completed / daily_hours
 ) * 100

completion_rate = min(
      completion_rate,
    100
)

st.subheader("🎯 Daily Progress")

st.progress(completion_rate / 100)

st.write(
     f"Completion Rate: {completion_rate:.1f}%"
 )

# Most Studied Subject
subject_summary = (
        progress_df.groupby("subject_name")["completed_hours"]
        .sum()
        .reset_index()
)
 
if not subject_summary.empty:

    best_subject = subject_summary.loc[
    subject_summary["completed_hours"].idxmax()
    ]

    st.success(
        f"🏆 Most Studied Subject: {best_subject['subject_name']}"
    )

    
    st.subheader("🥧 Study Time Distribution")

    fig2, ax2 = plt.subplots(figsize=(3, 3))  # Smaller chart

    explode = [0.03] * len(subject_summary)

    wedges, texts, autotexts = ax2.pie(
       subject_summary["completed_hours"],
       labels=subject_summary["subject_name"],
       autopct="%1.1f%%",
       startangle=90,
       explode=explode,
       shadow=True,
       pctdistance=0.75
    )

# Donut hole
    centre_circle = plt.Circle((0, 0), 0.55, fc="white")
    fig2.gca().add_artist(centre_circle)

# Total hours in center
    total_hours = subject_summary["completed_hours"].sum()

    ax2.text(
       0,
       0,
       f"{total_hours:.1f}\nHours",
       ha="center",
       va="center",
       fontsize=9,
       fontweight="bold"
    )

    ax2.set_title(
       "Study Hours",
       fontsize=10,
       fontweight="bold"
    )

    plt.tight_layout()

# Center the chart
    left, center, right = st.columns([1, 2, 1])

    with center:
       st.pyplot(fig2)
else:
    st.info("No subjects saved yet. Add a subject to generate a study timetable.")

st.markdown("---")

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

if not st.session_state.confirm_delete:

    if st.button("🗑️ Clear Database"):
        st.session_state.confirm_delete = True
        st.rerun()

else:
    st.warning("⚠️ Are you sure you want to clear the database?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, Clear Everything"):

            conn = sqlite3.connect("student.db")
            cursor = conn.cursor()

            cursor.execute("DELETE FROM subjects")
            cursor.execute("DELETE FROM progress")

            conn.commit()
            conn.close()

            st.session_state.confirm_delete = False

            st.success("Database Cleared Successfully!")
            st.rerun()

    with col2:
        if st.button("❌ Cancel"):
            st.session_state.confirm_delete = False
            st.rerun()