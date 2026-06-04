import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT,
    difficulty INTEGER,
    remaining INTEGER,
    exam_date TEXT,
    priority REAL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS progress(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT,
    study_date TEXT,
    completed_hours REAL
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")