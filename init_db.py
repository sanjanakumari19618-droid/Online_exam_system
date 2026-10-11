import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database.db")

conn   = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ─── Users Table ──────────────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    email    TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL
)
""")

# ─── Questions Table ───────────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    question       TEXT NOT NULL,
    option_a       TEXT NOT NULL,
    option_b       TEXT NOT NULL,
    option_c       TEXT NOT NULL,
    option_d       TEXT NOT NULL,
    correct_answer TEXT NOT NULL
)
""")

# ─── Results Table ────────────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    score        INTEGER NOT NULL,
    total        INTEGER NOT NULL,
    percentage   REAL    NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# ─── Sample Questions ─────────────────────────────────────────────────────────
cursor.execute("SELECT COUNT(*) FROM questions")
count = cursor.fetchone()[0]

if count < 10:
    # Clear old questions and re-insert full set
    cursor.execute("DELETE FROM questions")

    questions = [
        ("Python kya hai?",
         "Programming Language", "Database", "Operating System", "Browser",
         "a"),
        ("Web pages ko style karne ke liye kaun si language use hoti hai?",
         "Python", "HTML", "CSS", "Java",
         "c"),
        ("CPU ka full form kya hai?",
         "Central Processing Unit", "Computer Personal Unit",
         "Central Program Utility", "Core Processing Utility",
         "a"),
        ("Python mein text store karne ke liye kaun sa data type use hota hai?",
         "Integer", "Float", "String", "Boolean",
         "c"),
        ("HTML ka full form kya hai?",
         "HyperText Markup Language", "High Transfer Markup Language",
         "HyperText Management Language", "Home Tool Markup Language",
         "a"),
        ("Kaun sa HTML tag sabse bada heading banata hai?",
         "<h6>", "<head>", "<h1>", "<heading>",
         "c"),
        ("JavaScript mein block-scoped variable declare karne ke liye kaun sa keyword use hota hai?",
         "var", "let", "const", "function",
         "b"),
        ("CSS property jo text ka color change karti hai?",
         "background-color", "font-size", "margin", "color",
         "d"),
        ("HTTP ka full form kya hai?",
         "HyperText Transfer Protocol", "High Transfer Text Process",
         "Hyperlink Text Transport Program", "Home Tool Transfer Protocol",
         "a"),
        ("Array ke end mein element add karne ka JavaScript method kaun sa hai?",
         "append()", "push()", "add()", "insert()",
         "b"),
    ]

    cursor.executemany(
        "INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_answer) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        questions
    )
    print(f"[OK] {len(questions)} questions insert kiye gaye.")
else:
    print(f"[INFO] Questions table mein already {count} rows hain -- skip.")

conn.commit()
conn.close()
print("[OK] Database successfully initialize ho gaya!")
print(f"   DB Path: {DB_PATH}")
